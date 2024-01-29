from flask import Blueprint, jsonify

from src.settings import settings

blueprint_health = Blueprint("health", __name__)


@blueprint_health.route("/", methods=["GET"])
@blueprint_health.route("/health", methods=["GET"])
def get_application_state():
    return jsonify({"status": "OK", "version": settings.version})
