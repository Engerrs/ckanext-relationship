from __future__ import annotations

from typing import Any
from sqlalchemy.ext.declarative import declarative_base
import ckan.plugins.toolkit as tk

Base: Any

if hasattr(tk, "BaseModel"):
    Base = tk.BaseModel
else:
    Base = declarative_base()
