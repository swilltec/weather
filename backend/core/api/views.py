import json
from core.api.mixins import ClientFilteredQuerysetMixin
from core.api.serializers import (CitySerializer, ConversationSerializer,
                                  MessageSerializer, UserPreferenceSerializer)
from core.models import City, Client, Conversation, Message, UserPreference
from django.conf import settings
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, generics
from rest_framework import status
import logging
from core.utils.bot import WeatherAIService
from django.utils import timezone

weather_ai_service = WeatherAIService(
    api_key=settings.POE_API_KEY,
)


class BaseViewSet(ClientFilteredQuerysetMixin, ModelViewSet):
    filter_backends = [SearchFilter, OrderingFilter]


class CityViewSet(BaseViewSet):
    queryset = City.objects.select_related("client").order_by("-last_searched")
    serializer_class = CitySerializer
    search_fields = ["name", "country_code"]
    ordering_fields = ["last_searched", "search_count", "datetime_created"]


class ConversationViewSet(BaseViewSet):
    queryset = Conversation.objects.select_related("client").order_by(
        "-last_message_at"
    )
    serializer_class = ConversationSerializer
    search_fields = ["client__fingerprint"]
    ordering_fields = ["last_message_at", "message_count"]


    def create(self, request, *args, **kwargs):
        """Start a new conversation for a client. """
        
        # Create the conversation
        conversation = Conversation.objects.create(
            client=request.user,
            is_active=request.data.get('is_active', True)
        )
        
        # Serialize and return the response
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class MessageViewSet(BaseViewSet):
    queryset = Message.objects.select_related(
        "conversation", "conversation__client", "related_city"
    ).order_by("timestamp")
    serializer_class = MessageSerializer
    search_fields = ["content"]
    ordering_fields = ["timestamp"]


    def create(self, request, *args, **kwargs):
        """
        Send a message in a conversation and get AI response.
        

        Returns:
        - user_message: The user's message object
        - assistant_message: The AI's response message object
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = serializer.validated_data['conversation']
        user_message_content = serializer.validated_data['content']
        city_name = request.data.get('city')
        
       
        
        # Get related city if provided
        related_city = None
        if city_name:
            related_city, _ = City.objects.get_or_create(
                client=conversation.client,
                name=city_name,
                defaults={'search_count': 0}
            )
            related_city.search_count += 1
            related_city.last_searched = timezone.now()
            related_city.save()
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            message_type='user',
            content=user_message_content,
            related_city=related_city
        )
        
        # Get conversation history (last 20 messages for context)
        messages_history = Message.objects.filter(
            conversation=conversation
        ).order_by('timestamp')[:20]
        
        # Build messages for AI
        ai_messages = [weather_ai_service.get_system_prompt()]
        
        for msg in messages_history:
            if msg.message_type == 'user':
                ai_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.message_type == 'assistant':
                message_data = {
                    "role": "assistant",
                    "content": msg.content
                }
                
                ai_messages.append(message_data)
            elif msg.message_type == 'tool':
                ai_messages.append({
                    "role": "tool",
                    "content": msg.content
                })
        
        # Generate AI response
        try:
            ai_result = weather_ai_service.generate_response(ai_messages)
            
            # Save assistant message
            assistant_message = Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=ai_result['response'] or '',
                related_city=related_city
            )
            
            # Save tool results as separate messages
            tool_messages = []
            if ai_result['tool_results']:
                for tool_result in ai_result['tool_results']:
                    tool_message = Message.objects.create(
                        conversation=conversation,
                        message_type='tool',
                        content=json.dumps(tool_result['result']),
                        related_city=related_city
                    )
                    tool_messages.append(tool_message)
                
                # If there were tool calls, we need to get final response
                if ai_result['needs_continuation']:
                    # Add tool messages to history
                    ai_messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or '',
                    })
                    
                    for tool_msg in tool_messages:
                        ai_messages.append({
                            "role": "tool",
                            "content": tool_msg.content
                        })
                    
                    # Get final response after tool calls
                    final_result = weather_ai_service.generate_response(ai_messages)
                    
                    # Save final assistant message
                    final_message = Message.objects.create(
                        conversation=conversation,
                        message_type='assistant',
                        content=final_result['response'] or '',
                        related_city=related_city
                    )
                    
                    assistant_message = final_message
            
            # Update conversation metadata
            conversation.last_message_at = timezone.now()
            conversation.message_count = Message.objects.filter(
                conversation=conversation
            ).count()
            conversation.save()
            
            # Serialize response
            response_data = {
                "user_message": MessageSerializer(user_message).data,
                "assistant_message": MessageSerializer(assistant_message).data,
                "conversation": ConversationSerializer(conversation).data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Save error message
            error_message = Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=f"I apologize, but I encountered an error",
                related_city=related_city
            )
            logging.exception(e)
            
            return Response(
                {
                    "user_message": MessageSerializer(user_message).data,
                    "assistant_message": MessageSerializer(error_message).data
                },
                status=status.HTTP_201_CREATED
            )


class UserPreferenceViewSet(BaseViewSet):
    queryset = UserPreference.objects.select_related("client", "default_city")
    serializer_class = UserPreferenceSerializer
