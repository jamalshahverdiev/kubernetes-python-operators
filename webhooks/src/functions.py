from flask import jsonify
from base64 import b64encode
from json import dumps
from src.variables import Settings

def handle_mutate(request):
    request_info = request.get_json()

    uid = request_info["request"]["uid"]

    # Determine if we are handling a Pod or a Deployment
    if request_info["request"]["kind"]["kind"] == "Deployment":
        containers = request_info['request']['object']['spec']['template']['spec']['containers']
        base_path = "/spec/template/spec/containers/0"
    else:  # It's a Pod
        containers = request_info['request']['object']['spec']['containers']
        base_path = "/spec/containers/0"

    # Check if the 'env' key is present in the first container. If not, add it.
    if 'env' not in containers[0]:
        path = f"{base_path}/env"
        value = [{"name": Settings.env_key, "value": Settings.env_value}]
    else:
        # Check if `Settings.env_key` is already present in the environment variables
        if any(env_var.get('name') == Settings.env_key for env_var in containers[0]['env']):
            # If `Settings.env_key` is already present, we don't need to do anything
            return jsonify({"apiVersion": "admission.k8s.io/v1", "kind": "AdmissionReview", "response": {"uid": uid, "allowed": True}})
        else:
            path = f"{base_path}/env/-"
            value = {"name": Settings.env_key, "value": Settings.env_value}

    patch = [
        {
            "op": "add",
            "path": path,
            "value": value
        }
    ]

    patch_bytes = bytes(dumps(patch), "utf-8")
    patch_b64 = b64encode(patch_bytes).decode("utf-8")

    admission_response = {
        "uid": uid,
        "allowed": True,
        "patch": patch_b64,
        "patchType": "JSONPatch"
    }

    admission_review = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": admission_response
    }

    return jsonify(admission_review)


def handle_validate(request):
    request_info = request.get_json()

    uid = request_info["request"]["uid"]
    if request_info["request"]["kind"]["kind"] == "Deployment":
        labels = request_info['request']['object']['spec']['template']['metadata']['labels']
    else:  # It's a Pod
        labels = request_info['request']['object']['metadata'].get('labels', {})

    if 'version' not in labels:
        admission_response = {
            "uid": uid,
            "allowed": False,
            "status": {
                "message": Settings.validate_response_message
            }
        }
    else:
        admission_response = {
            "uid": uid,
            "allowed": True
        }

    admission_review = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": admission_response
    }

    return jsonify(admission_review)

