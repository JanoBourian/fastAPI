description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** @janobourian.
* **Read users** @janobourian.
"""

tags_metadata = [
    {
        "name": "books",
        "description": "Operations with books. The **login** logic is also here.",
    },
    {"name": "readers", "description": "Operation with readers"},
    {
        "name": "register",
        "description": "Operation to create readers",
    },
    {
        "name": "read",
        "description": "Operation to create relation between books and readers",
    },
    {
        "name": "token",
        "description": "Operation to login",
    },
    {
        "name": "me",
        "description": "Information about current user",
    },
    {
        "name": "users",
        "description": "Information about all users",
    },
    {
        "name": "authors",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

information = {
    "title": "janobourian",
    "description": description,
    "summary": "Store app",
    "version": "0.0.1",
    "redoc_url": None,
    # "docs_url": None,
    # "openapi_url": None,
    "terms_of_service": "https://example.com/terms/",
    "contact": {"name": "janobourian", "url": "https://example.com/contact/"},
    "license_info": {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    "openapi_tags": tags_metadata,
}
