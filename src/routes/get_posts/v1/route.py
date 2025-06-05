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
    # print(content_object_names, type(content_object_names))

    
# Loop through each content_object_name in the list
    for content_object_name in content_object_names:
        # print("Looping content_object_name:", content_object_name)  # Show which content object is currently being processed

        # If the current content object is "users", fetch all users
        if content_object_name == "users":
            print("Fetching users from API...")  # Debug message to indicate user fetching has started

            # Send a GET request to the fake store API to retrieve all users
            users = requests.get("https://fakestoreapi.com/users")
            
            # Parse the JSON response into Python list of dictionaries
            users = users.json()
            # print("users:", users)  # Output the list of users fetched

            # Format each user as a dict with "value" as the user ID and "label" as the username
            data = [
                {"value": str(user["id"]), "label": str(user["username"])} for user in users
            ]

            # Append the formatted user data into the content_objects list
            content_objects.append({
                "content_object_name": "users",
                "data": data
            })

            print("content_object_names processed:", content_object_names)  # Print the processed content object names
            print("form_data:", form_data)  # Print the form data received

        # If the current content object is one of the address fields, fetch user details
        elif content_object_name in ["city", "street", "number"]:
            # Get the user ID from form_data (selected user)
            user_id = form_data.get("user")
            # print("user_id:", user_id)  # Print the user ID to verify it's being retrieved

            if user_id:
                # Fetch detailed user info from the fake store API using the user ID
                user_details = requests.get(f"https://fakestoreapi.com/users/{user_id}")
                
                # Get the "address" field from the response
                address = user_details.json().get("address", {})
                # print("line120", address)  # Print the address to confirm it's correct

                # Depending on the content_object_name, return only the specific address field
                if content_object_name == "city":
                    content_objects.append({
                        "content_object_name": "city",
                        "data": [{"value": address.get("city"), "label": address.get("city")}]
                    })
                elif content_object_name == "street":
                    content_objects.append({
                        "content_object_name": "street",
                        "data": [{"value": address.get("street"), "label": address.get("street")}]
                    })
                elif content_object_name == "number":
                    content_objects.append({
                        "content_object_name": "number",
                        "data": [{"value": str(address.get("number")), "label": str(address.get("number"))}]
                    })

    return Response(data={"content_objects": content_objects})


# @router.route("/user/details", methods=["GET, POST"])
# def get_users_details():
#     """
#     This is an example of a route that can be used to fetch details of a user.
#     It can be used in the /content route to fetch details of a user when the user is selected in a dynamic form field.
#     """
#     request = Request(flask_request)
#     data = request.data

#     user_id = data.get("user_id")
    
#     if not user_id:
#         return Response(data={"error": "User ID is required"}, status_code=400)

#     response = requests.get(f"https://fakestoreapi.com/users/{user_id}")
    
#     if response.status_code != 200:
#         return Response(data={"error": "User not found"}, status_code=404)

#     user_details = response.json()
    
#     return Response(data=user_details)