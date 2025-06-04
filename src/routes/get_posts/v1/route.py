from workflows_cdk import Response, Request
from flask import request as flask_request
from main import router
import requests

# @router.route("/ping", methods=["GET"])
# def ping():
#     return "pong"

@router.route("/execute", methods=["GET", "POST"])
def execute():
    """
    This is the function that is executed when you click on "Run" on a workflow that uses this action.
    """
    request = Request(flask_request)

    # The data object of request.data will contain all of the fields filled in the form and defined in the schema.json file.
    data = request.data

    platform = data.get("platform")
    post_type = data.get("post_type")
    api_key = data.get("api_key")

    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    url = "https://fakestoreapi.com/products"  # Example URL, replace with actual API endpoint

    if platform == "instagram":
        url = url
    elif platform == "facebook":
        url = url

    response = requests.get(url, headers=headers)
    response = response.json()
    # Your logic here
    # Here you can add your logic to execute the action which may consist of, for example:
    # - calling an API
    # - doing some calculations
    # - doing some data transformations
    # - validating data
    

    output = response

    return Response(data=output, metadata={"affected_rows": len(output)})


@router.route("/content", methods=["GET", "POST"])
def content():
    """
    This is the function that goes and fetches the necessary data to populate the possible choices in dynamic form fields.
    For example, if you have a module to delete a contact, you would need to fetch the list of contacts to populate the dropdown
    and give the user the choice of which contact to delete.

    An action's form may have multiple dynamic form fields, each with their own possible choices. Because of this, in the /content route,
    you will receive a list of content_object_names, which are the identifiers of the dynamic form fields. A /content route may be called for one or more content_object_names.

    Every data object takes the shape of:
    {
        "value": "value",
        "label": "label"
    }
    
    Args:
        data:
            form_data:
                form_field_name_1: value1
                form_field_name_2: value2
            content_object_names:
                [
                    {   "id": "users"   }
                ]
        credentials:
            connection_data:
                value: (actual value of the connection)

    Return:
        {
            "content_objects": [
                {
                    "content_object_name": "users",
                    "data": [{"value": "value1", "label": "label1"}]
                },
                ...
            ]
        }
    """
    request = Request(flask_request)

    data = request.data

    form_data = data.get("form_data", {})
    content_object_names = data.get("content_object_names", [])
    
    # Extract content object names from objects if needed
    if isinstance(content_object_names, list) and content_object_names and isinstance(content_object_names[0], dict):
        content_object_names = [obj.get("id") for obj in content_object_names if "id" in obj]

    content_objects = [] # this is the list of content objects that will be returned to the frontend
    print(content_object_names, type(content_object_names))

    for content_object_name in content_object_names:
        if content_object_name == "users":
            # logic here
            users = requests.get("https://fakestoreapi.com/users")
            users = users.json()
            data = [
                {"value": str(user["id"]), "label": str(user["username"])} for user in users
            ]
            content_objects.append({
                    "content_object_name": "users",
                    "data": data
                })
    
    return Response(data={"content_objects": content_objects})
