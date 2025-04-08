from flask import Flask, request, Response, jsonify
from flask_restful import Resource, Api
from loguru import logger
from config.logging_setup import setup_logging
from config.config_setup import init_config
import json
import asyncio
from brain.domain_router import DomainRouter

app = Flask(__name__)
api = Api(app)
# Load and validate configuration
config = init_config()

# Initialize domain router with validated config
domain_router = DomainRouter(config)

class Dialog(Resource):
    def post(self, dialog_id):
        ## -- The following should match the parameters sent from the interface -- ##
        # Get parameters from the request
        sender = request.form['sender']
        persona_selected = request.form['persona_selected']
        messages = json.loads(request.form['messages'])  # Get full message history
        # upload_dir = request.form.get('upload_dir')  # Make upload_dir optional
        
        logger.debug(f"Received request with parameters - {dialog_id=}, {sender=}, {persona_selected=}, {messages=}")
         ## End: The following should match the parameters sent from the interface -- ##

        try:
            # Get or create handler for this persona
            handler = domain_router.get_handler(persona_selected)

            # Get the streaming response from the handler
            response_stream = handler.chat(messages, stream=True)
            
            # Simplified streaming function
            def generate():
                accumulated_message = {'role': 'assistant', 'content': ''}
                
                # Use asyncio.run to handle the async iterator
                async def process_stream():
                    try:
                        async for chunk in response_stream:
                            if isinstance(chunk, dict) and 'message' in chunk:
                                if chunk.get('is_chunk', False):
                                    content = chunk['message']
                                    accumulated_message['content'] += content
                                    response_data = {
                                        'dialog_id': dialog_id, 
                                        'message': content, 
                                        'sender': sender, 
                                        'is_chunk': True
                                    }
                                    yield f"data: {json.dumps(response_data)}\n\n"
                        
                        # Final message
                        final_data = {
                            'dialog_id': dialog_id, 
                            'message': accumulated_message['content'], 
                            'sender': sender, 
                            'is_chunk': False
                        }
                        yield f"data: {json.dumps(final_data)}\n\n"
                        yield "data: [DONE]\n\n"
                    except Exception as e:
                        logger.error(f"Error in processing stream: {str(e)}")
                        raise
                
                # Use a single event loop for the entire stream processing
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    async_gen = process_stream()
                    while True:
                        try:
                            # Get the next chunk from our async generator
                            chunk = loop.run_until_complete(anext(async_gen))
                            yield chunk
                        except StopAsyncIteration:
                            break
                except Exception as e:
                    logger.error(f"Error in generate: {str(e)}")
                    raise
                finally:
                    loop.close()
            
            return Response(generate(), mimetype='text/event-stream')
        except Exception as e:
            logger.error(f"Error in post: {str(e)}")

api.add_resource(Dialog, '/<string:dialog_id>')

def cleanup():
    """Cleanup function to be called when the server shuts down."""
    try:
        logger.info("Starting server cleanup")
        # domain_router.close()
        # service_manager.close_all()
        logger.info("Server cleanup completed")
    except Exception as e:
        logger.error(f"Error during server cleanup: {str(e)}")

if __name__ == '__main__':
    print("Starting artmind brain server...")
    setup_logging()
    try:
        app.run(debug=True, port="5010")
    finally:
        cleanup()