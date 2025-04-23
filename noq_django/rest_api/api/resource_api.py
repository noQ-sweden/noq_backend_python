from ninja import Router, Schema
from ninja.errors import HttpError
from django.db import models
from django.utils import timezone
from typing import List, Optional
from django.shortcuts import get_object_or_404
from backend.models import Resource
from .api_schemas import ResourceSchema, ResourcePostSchema, ResourcePatchSchema
from backend.auth import group_auth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ninja import Query
from pydantic import BaseModel
from typing import Optional
from ninja import Schema
from typing import List
from datetime import datetime

class ResourceSchema(Schema):
    id: int
    name: str
    opening_time: str
    closing_time: str
    address: str
    phone: str
    email: str
    target_group: str
    other: str
    applies_to: List[str]
    is_open_now: bool  # ✅ Add this line


class ResourceQuerySchema(BaseModel):
    search: Optional[str] = None
    open_now: Optional[bool] = None
    eu_citizen: Optional[bool] = None
    target_group: Optional[List[str]] = None
    applies_to: Optional[List[str]] = None
    sort: Optional[str] = None
    
# List of EU countries for filtering
EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
]

# Create router without authentication for public access
router = Router(tags=["Resources"])  # for authenticated routes
public_router = Router(auth=None, tags=["Resources"])  # for Swagger testing (no auth)


@router.get("/", response=List[ResourceSchema], tags=["Resources"])
@csrf_exempt
def list_resources(request, filters: ResourceQuerySchema = Query(...)):
    """
    List all resources with optional filtering
    """
    try:
        resources = Resource.objects.all()
        
        # Apply search filter
        if filters.search and filters.search.strip():
            resources = resources.filter(name__icontains=filters.search.strip())

        # Apply open now filter
        if filters.open_now is True:
            current_time = datetime.now().time()

            def parse_time(t):
                if isinstance(t, str):
                    return datetime.strptime(t, '%H:%M:%S').time()
                return t

            resources = [
                r for r in resources
                if parse_time(r.opening_time) <= current_time <= parse_time(r.closing_time)
            ]

        # Apply EU citizen filter
        if filters.eu_citizen is True:
            resources = [r for r in resources if any(country.lower() in r.address.lower() for country in EU_COUNTRIES)]

        # Apply target group filter
        if filters.target_group and any(filters.target_group):
            resources = [r for r in resources if r.target_group in filters.target_group]

        # Apply applies_to filter
        if filters.applies_to and any(filters.applies_to):
            resources = [r for r in resources if any(tag in r.applies_to for tag in filters.applies_to)]

        # Apply sorting
        if filters.sort and filters.sort in ['name', '-name']:
            reverse = filters.sort.startswith('-')
            resources = sorted(resources, key=lambda r: r.name.lower(), reverse=reverse)
        
        # Create a list to store processed resources
        processed_resources = []
        
        # Process each resource
        for resource in resources:
            # Create a dictionary with resource data
            resource_dict = {
                'id': resource.id,
                'name': resource.name,
                'opening_time': resource.opening_time.strftime('%H:%M:%S'),
                'closing_time': resource.closing_time.strftime('%H:%M:%S'),
                'address': resource.address,
                'phone': resource.phone,
                'email': resource.email,
                'target_group': resource.target_group,
                'other': resource.other,
                'applies_to': resource.applies_to,
                'is_open_now': resource.is_open_now()
            }
            
            # Add to the processed list
            processed_resources.append(resource_dict)
        
        return [ResourceSchema(**resource_dict) for resource_dict in processed_resources]
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@router.get("/{resource_id}", response=ResourceSchema, tags=["Resources"])
@csrf_exempt
def get_resource(request, resource_id: int):
    """
    Get a specific resource by ID
    """
    try:
        resource = get_object_or_404(Resource, id=resource_id)
        
        # Create a dictionary with resource data
        resource_dict = {
            'id': resource.id,
            'name': resource.name,
            'opening_time': str(resource.opening_time),
            'closing_time': str(resource.closing_time),
            'address': resource.address,
            'phone': resource.phone,
            'email': resource.email,
            'target_group': resource.target_group,
            'other': resource.other,
            'applies_to': resource.applies_to,
            'is_open_now': resource.is_open_now()
        }
        
        return resource_dict
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# Protected endpoints (require authentication)
@public_router.post("/", response={201: ResourceSchema})
def create_resource_public(request, payload: ResourcePostSchema):
    try:
        # Convert string times to datetime.time objects
        opening_time = datetime.strptime(payload.opening_time, '%H:%M:%S').time()
        closing_time = datetime.strptime(payload.closing_time, '%H:%M:%S').time()

        # Create the resource
        resource = Resource.objects.create(
            name=payload.name,
            opening_time=opening_time,
            closing_time=closing_time,
            address=payload.address,
            phone=payload.phone,
            email=payload.email,
            target_group=payload.target_group,
            other=payload.other,
            applies_to=payload.applies_to
        )
        return 201, {
            'id': resource.id,
            'name': resource.name,
            'opening_time': str(resource.opening_time),
            'closing_time': str(resource.closing_time),
            'address': resource.address,
            'phone': resource.phone,
            'email': resource.email,
            'target_group': resource.target_group,
            'other': resource.other,
            'applies_to': resource.applies_to,
            'is_open_now': resource.is_open_now()
        }
    except Exception as e:
        raise HttpError(400, str(e))

@router.patch("/{resource_id}", response=ResourceSchema, tags=["Resources"], auth=lambda request: group_auth(request, "user"))
def update_resource(request, resource_id: int, payload: ResourcePatchSchema):
    """
    Update an existing resource
    """
    resource = get_object_or_404(Resource, id=resource_id)
    
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(resource, field, value)
    
    try:
        resource.save()
        
        # Create a dictionary with resource data
        resource_dict = {
            'id': resource.id,
            'name': resource.name,
            'opening_time': resource.opening_time.strftime('%H:%M:%S'),
            'closing_time': resource.closing_time.strftime('%H:%M:%S'),
            'address': resource.address,
            'phone': resource.phone,
            'email': resource.email,
            'target_group': resource.target_group,
            'other': resource.other,
            'applies_to': resource.applies_to,
            'is_open_now': resource.is_open_now()
        }
        
        return resource_dict
    except Exception as e:
        raise HttpError(400, str(e))

@router.delete("/{resource_id}", response={204: None}, tags=["Resources"], auth=lambda request: group_auth(request, "user"))
def delete_resource(request, resource_id: int):
    """
    Delete a resource
    """
    resource = get_object_or_404(Resource, id=resource_id)
    resource.delete()
    return 204, None 