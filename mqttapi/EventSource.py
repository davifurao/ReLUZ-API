from flask import Flask, Response, render_template
from flask_cors import CORS
from json_manipulator import JSONManipulator

class ServerSideEvents:
    def __init__(self, app_name=__name__):
        self.app_name = app_name
        self.app = Flask(app_name)
        self.routes = {}
        self.server_started = False
        self.json = JSONManipulator()  # Criar instância do JSONManipulator aqui
        self.configureEventSource()

    def configureEventSource(self, port=5000, debug=True):
        self.port = port
        self.debug = debug
        CORS(self.app)

    def render_template(self, path_file):
        return render_template(path_file)

    def start_server(self):
        self.app.run(port=self.port, debug=self.debug)
        self.server_started = True

    def createRoute(self, route_name, function):
        if route_name not in self.routes:
            self.routes[route_name] = function

    def add_route(self, route_name, function):
        if route_name not in self.routes:
            self.routes[route_name] = function
            self.app.route(f'/{route_name}')(function)

    def create_custom_route(self, route_name, mqtt_message):
        @self.app.route(f'/{route_name}')
        def custom_route_function():
            return self.stream_mqtt(mqtt_message)

    def stream_mqtt(self, mqtt_message):
        def mqttSend():
            while True:
                event = f"data:{self.json.createMQTTjson(mqtt_message)}\n\n"
                yield event
        return Response(mqttSend(), content_type='text/event-stream')

    def sendMQTTmessage(self, mqtt_message, route_name='stream'):
        if not self.server_started:
            self.start_server()

        @self.app.route(f'/{route_name}')
        def streams_mqtt():
            def mqttSend():
                while True:
                    event = f"data:{self.json.createMQTTjson(mqtt_message)}\n\n"
                    yield event
            return Response(mqttSend(), content_type='text/event-stream')
