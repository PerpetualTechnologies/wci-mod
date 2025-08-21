# Copyright 2024 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Chattigo Partner implementation
"""

import logging
import re
from typing import Optional
from partners import Partner


class Lead:
    """Simple Lead class for storing lead information."""
    def __init__(self, phone: str, protocol: str):
        self.phone = phone
        self.protocol = protocol
        self.message_id = ""
        self.conversation_id = ""
        self.timestamp = None


class ChattigoPartner(Partner):
    """
    Partner implementation for Chattigo BSP
    """
    
    def process_message(self, payload):
        """
        Process message from Chattigo webhook.
        This is the required abstract method from Partner base class.
        
        Args:
            payload: The webhook payload from Chattigo
            
        Returns:
            Lead: Processed lead data or None if processing fails
        """
        try:
            # Extraer información del mensaje
            message_data = self._extract_message_data(payload)
            
            # Obtener número de teléfono
            phone = self._get_phone_number(message_data)
            
            # Obtener texto del mensaje
            message_text = self._get_message_text(message_data)
            
            # Extraer protocolo del mensaje
            protocol = self._get_protocol(message_text)
            
            if not protocol:
                logging.warning(f"No se encontró el protocolo en el mensaje de Chattigo: {message_text}")
                return None
            
            if not phone:
                logging.warning(f"No se encontró el número de teléfono en el mensaje de Chattigo")
                return None
            
            # Crear el objeto Lead
            lead = Lead(phone=phone, protocol=protocol)
            
            # Agregar información adicional del webhook
            lead.message_id = message_data.get('id', '')
            lead.conversation_id = message_data.get('conversation_id', '')
            lead.timestamp = message_data.get('timestamp')
            
            # Logging para debugging
            logging.info(f"Protocolo {lead.protocol} asociado al teléfono {lead.phone}")
            
            return lead
            
        except Exception as e:
            logging.error(f"Error al procesar el JSON de Chattigo: {str(e)}")
            return None

    def _extract_message_data(self, payload: dict) -> dict:
        """Extrae los datos del mensaje del payload de Chattigo."""
        if 'message' in payload:
            return payload['message']
        elif 'messages' in payload and len(payload['messages']) > 0:
            return payload['messages'][0]
        elif 'data' in payload and 'message' in payload['data']:
            return payload['data']['message']
        else:
            return payload

    def _get_phone_number(self, message_data: dict) -> str:
        """Extrae el número de teléfono del mensaje."""
        phone_fields = ['from', 'phone', 'phone_number', 'sender', 'contact_phone', 'phoneNumber']
        
        for field in phone_fields:
            if field in message_data and message_data[field]:
                phone = str(message_data[field])
                # Limpiar el número de teléfono
                return re.sub(r'[^\d+]', '', phone)
        
        return ""

    def _get_message_text(self, message_data: dict) -> str:
        """Extrae el texto del mensaje."""
        text_fields = ['text', 'body', 'content', 'message', 'text_body']
        
        for field in text_fields:
            if field in message_data:
                if isinstance(message_data[field], dict):
                    if 'body' in message_data[field]:
                        return message_data[field]['body']
                elif isinstance(message_data[field], str):
                    return message_data[field]
        
        return ""

    def _get_protocol(self, message: str) -> Optional[str]:
        """
        Busca y extrae el protocolo del cuerpo del mensaje.
        Busca el patrón [Chat ID: ...]
        """
        if not message:
            return None
            
        # Patrón principal: [Chat ID: ...]
        match = re.search(r"\[Chat ID: (.+?)\]", message)
        if match:
            return match.group(1).strip()
        
        # Patrones alternativos
        patterns = [
            r"WCI_([A-Za-z0-9]+)",
            r"Protocolo: ?([A-Za-z0-9]+)",
            r"ID: ?([A-Za-z0-9]+)",
            r"#([A-Za-z0-9]{6,})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        return None


