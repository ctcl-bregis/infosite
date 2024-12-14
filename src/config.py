# InfoSite - CTCL 2024
# File: /infosite/config.py
# Purpose: Configuration models
# Created: November 23, 2024
# Modified: December 2, 2024

import json
import logging
import os
from markdown import markdown
from datetime import datetime
from enum import Enum, IntEnum
from typing import Dict, Any, List, Union, get_origin
from typing_extensions import Annotated

from pydantic import BaseModel, PositiveInt, ValidationError, Field, SkipValidation
from pydantic.color import Color

from src.utils import mdpath2html
from lysine import Environment, FileSystemLoader


logger = logging.getLogger(__name__)

class PageSectionContent(BaseModel):
    type: str = Field("content")
    # Should the section be within a box? 
    # This may be removed soon
    boxed: bool
    title: str
    theme: str
    # Should the section have a minimum height of the viewport?
    # This may be removed soon
    fitscreen: bool
    content: str

class SectionLinklistItemTitleCustom(BaseModel):
    type: str = Field("titlecustom")
    title: str
    theme: str
    link: str

class SectionLinklistItemTitle(BaseModel):
    type: str = Field("title")
    page: str

class SectionLinklistItemFullCustom(BaseModel):
    type: str = Field("fullcustom")
    title: str
    theme: str
    startdate: Union[datetime | None]
    enddate: Union[datetime | None]
    dateprecision: str
    desc: str
    icon: Union[str | None]
    icontitle: Union[str | None]

class SectionLinklistItemFull(BaseModel):
    type: str = Field("full")
    page: str

class SectionLinklist(BaseModel):
    type: str = Field("linklist")
    # Should the section be within a box? 
    # This may be removed soon
    boxed: bool
    title: str
    theme: str
    # Should the section have a minimum height of the viewport?
    # This may be removed soon
    fitscreen: bool
    links: List[Union[SectionLinklistItemTitleCustom, SectionLinklistItemTitle, SectionLinklistItemFullCustom, SectionLinklistItemFull]]

class PageConfig(BaseModel):
    title: str
    theme: str
    startdate: Union[datetime | None]
    enddate: Union[datetime | None]
    dateprecision: str
    desc: str
    icon: Union[str | None]
    icontitle: Union[str | None]
    favicon: Union[str | None]
    content: Dict[str, Union[PageSectionContent, SectionLinklist]]


#class LoggerConfig(BaseModel):
#    enable: bool

def loadtemplates():
    return
    

class Theme(BaseModel):
    dispname: str
    color: Color
    fgcolor: Color
    themedir: str
    tmplenv: Environment = Field(default_factory = loadtemplates)

    class Config:
        arbitrary_types_allowed = True

class SiteConfigThemes(BaseModel):
    default: str
    minimizehtml: bool
    minimizecss: bool
    themes: dict[str, Theme]

class NavbarItem(BaseModel):
    title: str
    link: str

class LogLevelEnum(str, Enum):
    error = "error"
    warn = "warn"
    info = "info"
    debug = "debug"

class SiteConfig(BaseModel):
    bindip: str
    bindport: int
    domain: str
    loglevel: LogLevelEnum
    dateformats: Dict[str, str]
    navbar: List[NavbarItem]
#    logger: LoggerConfig
    redirects: Dict[str, str]
    themeconfig: SiteConfigThemes

def loadconfig(path) -> SiteConfig | None:
    path = path + "config.json"

    if os.path.exists(path):
        with open(path) as f:
            configtxt = f.read()
    else:
        logger.error(f"File {path}/config.json not found")
        logger.info(f"Current working directory {os.getcwd()}")
        return None

    try:
        configjson = json.loads(configtxt)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return None

    try:
        config = SiteConfig(**configjson)
    except ValidationError as e:
        logger.error(e.errors())
        return None

    return config

def loadpages(path) -> Dict[str, PageConfig]:
    pages = {}

    for root in os.walk(path):
        pagepath = root[0]
        jsonpath = f"{pagepath}/page.json"

        print(pagepath)
        print(jsonpath)

        if os.path.exists(f"{pagepath}/.placeholder"):
            logger.info(f"Path {pagepath} has file .placeholder, skipping")
            continue

        if os.path.exists(jsonpath):
            with open(jsonpath) as f:
                jsontxt = f.read()
        else:
            logger.warn(f"Path {pagepath} does not have a page.json, skipping")
            continue
            
        try:
            configjson = json.loads(jsontxt)
        except Exception as e:
            logger.warn(f"Failed to load {jsonpath}: {e}")
            continue
            
        try:
            config = PageConfig(**configjson)
        except ValidationError as e:
            logger.warn(f"Failed to deserialize {jsonpath}: {e.errors()}")
            continue
        
        # Pre-render markdown files
        # TODO: Probably should have this somewhere else
        for section, content in config.content.items():
            if isinstance(content, PageSectionContent):
                mdpath2html(pagepath + content.content)

        pagepath = pagepath.replace(path, "")
        pagepath += "/"

        pages[pagepath] = config
        

    return pages
