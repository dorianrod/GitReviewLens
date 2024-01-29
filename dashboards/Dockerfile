FROM grafana/grafana-dev:10.2.0-133119

# Make it as simple as possible to access the grafana instance for development purposes
# Do NOT enable these settings in a public facing / production grafana instance
ENV GF_AUTH_ANONYMOUS_ORG_ROLE "Admin"
# Set development mode so plugins can be loaded without the need to sign
ENV GF_DEFAULT_APP_MODE "development"

ENV GF_AUTH_BASIC_ENABLED "true"
ENV GF_SECURITY_ADMIN_PASSWORD "admin"
ENV GF_SECURITY_ADMIN_USER "admin"

ENV GF_LOG_LEVEL "debug"

RUN grafana-cli plugins install grafana-mongodb-datasource
RUN grafana-cli plugins install marcusolsson-json-datasource
RUN grafana-cli plugins install speakyourcode-button-panel
RUN grafana-cli plugins install volkovlabs-variable-panel
RUN grafana-cli plugins install cloudspout-button-panel
RUN grafana-cli plugins install isaozler-paretochart-panel
RUN grafana-cli plugins install volkovlabs-echarts-panel

# Inject livereload script into grafana index.html
USER root
RUN sed -i 's/<\/body><\/html>/<script src=\"http:\/\/localhost:35729\/livereload.js\"><\/script><\/body><\/html>/g' /usr/share/grafana/public/views/index.html