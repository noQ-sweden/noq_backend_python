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

# List of EU countries for filtering
EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
]

# Create router without authentication for public access
router = Router()

@router.get("/", response=List[ResourceSchema], tags=["Resources"])
@csrf_exempt
def list_resources(request, 
                  search: str = None,
                  open_now: bool = None,
                  eu_citizen: bool = None,
                  target_group: List[str] = None,
                  applies_to: List[str] = None,
                  sort: str = None):
    """
    List all resources with optional filtering
    """
    try:
        resources = Resource.objects.all()
        
        # Apply search filter
        if search:
            resources = resources.filter(name__icontains=search)
        
        # Apply open now filter
        if open_now:
            resources = [r for r in resources if r.is_open_now()]
        
        # Apply EU citizen filter
        if eu_citizen:
            resources = [r for r in resources if any(country.lower() in r.address.lower() for country in EU_COUNTRIES)]
        
        # Apply target group filter
        if target_group:
            resources = [r for r in resources if r.target_group in target_group]
        
        # Apply applies_to filter
        if applies_to:
            resources = [r for r in resources if any(tag in r.applies_to for tag in applies_to)]
        
        # Apply sorting
        if sort in ['name', '-name']:
            reverse = sort.startswith('-')
            resources = sorted(resources, key=lambda r: r.name.lower(), reverse=reverse)
        
        return resources
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
        return resource
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# Protected endpoints (require authentication)
@router.post("/", response={201: ResourceSchema}, tags=["Resources"], auth=lambda request: group_auth(request, "user"))
def create_resource(request, payload: ResourcePostSchema):
    """
    Create a new resource
    """
    try:
        resource = Resource.objects.create(
            name=payload.name,
            opening_time=payload.opening_time,
            closing_time=payload.closing_time,
            address=payload.address,
            phone=payload.phone,
            email=payload.email,
            target_group=payload.target_group,
            other=payload.other,
            applies_to=payload.applies_to
        )
        return 201, resource
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
        return resource
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