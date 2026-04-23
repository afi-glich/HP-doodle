from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("events.urls")),
]
```

Create `backend/events/urls.py`:

```python
# backend/events/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
]
```

### 0.4.8 — Create a health-check endpoint

Replace `backend/events/views.py` with:

```python
# backend/events/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health_check(request):
    """Simple endpoint to verify the API is running."""
    return Response({
        "status": "ok",
        "message": "Doodle Clone API is running.",
    })
