"""FastAPI server endpoints for data-table-related queries."""
import shutil
from pathlib import Path
from urllib import parse

from fastapi import APIRouter, Depends, HTTPException, Request, status

import zeno_backend.database.copy as copy
import zeno_backend.database.delete as delete
import zeno_backend.database.insert as insert
import zeno_backend.database.select as select
import zeno_backend.database.update as update
import zeno_backend.util as util
from zeno_backend.classes.project import (
    Project,
    ProjectCopy,
    ProjectState,
)
from zeno_backend.classes.user import Organization, User

router = APIRouter(tags=["zeno"])


@router.get("/project-public/{project_uuid}", response_model=bool, tags=["zeno"])
async def is_project_public(project_uuid: str, request: Request):
    """Check if a given project is public.

    Args:
        project_uuid (str): uuid of the project to be checked.
        request (Request): http request to get user information from.

    Returns:
        bool: whether the specified project is public.
    """
    await util.project_access_valid(project_uuid, request)
    return select.project_public(project_uuid)


@router.get("/project-state/{project_uuid}", response_model=ProjectState, tags=["zeno"])
async def get_project_state(
    project_uuid: str,
    request: Request,
):
    """Get the current state of a project.

    Args:
        project_uuid (str): uuid of the project to fetch the state for.
        request (Request): http request to get user information from.

    Raises:
        HTTPException: error if the state cannot be fetched.

    Returns:
        ProjectState | None: current state of the project.
    """
    await util.project_access_valid(project_uuid, request)
    project = await select.project_from_uuid(project_uuid)
    user = await util.get_user_from_token(request)
    return await select.project_state(project_uuid, user, project)


@router.get(
    "/project-uuid/{owner_name}/{project_name}",
    response_model=str,
    tags=["zeno"],
)
async def get_project_uuid(owner_name: str, project_name: str, request: Request):
    """Get the UUID of a project by owner and project name.

    Args:
        owner_name (str): name of the project's owner.
        project_name (str): name of the project.
        request (Request): http request to get user information from.

    Raises:
        HTTPException: error if the project uuid could not be fetched.

    Returns:
        str: uuid of the requested project.
    """
    uuid = await select.project_uuid(owner_name, parse.unquote(project_name))
    if uuid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "ERROR: Project " + owner_name + "/" + project_name + " does not exist."
            ),
        )
    await util.project_access_valid(uuid, request)
    return uuid


@router.get(
    "/projects",
    response_model=list[Project],
    tags=["zeno"],
)
async def get_projects(current_user=Depends(util.auth.claim())):
    """Get all projects for the current user.

    Args:
        current_user (Any, optional): User requesting all projects.
            Defaults to Depends(util.auth.claim()).

    Returns:
        list[Project]: all project of the user who sent the request.
    """
    user = await select.user(current_user["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=("User not logged in"),
        )
    return await select.projects(user)


@router.post("/like-project/{project_uuid}", tags=["zeno"])
async def like_project(project_uuid: str, current_user=Depends(util.auth.claim())):
    """Like a project.

    Args:
        project_uuid (str): UUID of the project to be liked.
        current_user (Any, optional): user liking the project.
            Defaults to Depends(util.auth.claim()).
    """
    user = await select.user(current_user["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=("User not logged in"),
        )
    await insert.like_project(user.id, project_uuid)


@router.get(
    "/project-users/{project_uuid}",
    response_model=list[User],
    tags=["zeno"],
    dependencies=[Depends(util.auth)],
)
async def get_project_users(project_uuid: str, request: Request):
    """Get all users of a specific project.

    Args:
        project_uuid (str): UUID of the project to get all users for.
        request (Request): http request to get user information from.

    Returns:
        list[User]: all users who have access to the project.
    """
    await util.project_editor(project_uuid, request)
    return await select.project_users(project_uuid)


@router.get(
    "/project-organizations/{project_uuid}",
    response_model=list[Organization],
    tags=["zeno"],
    dependencies=[Depends(util.auth)],
)
async def get_project_orgs(project_uuid: str, request: Request):
    """Get all organizations that have access to a project.

    Args:
        project_uuid (str): UUID of the project to get all organizations for.
        request (Request): http request to get user information from.

    Returns:
        list[Organization]: all organizations with access to the project.
    """
    await util.project_editor(project_uuid, request)
    return await select.project_orgs(project_uuid)


@router.post(
    "/project-user/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def add_project_user(project_uuid: str, user: User, request: Request):
    """Add a user to a project.

    Args:
        project_uuid (str): UUID of the project to add a new user to.
        user (User): user to be added to the project.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project_uuid, request)
    project_obj = await select.project_from_uuid(project_uuid)
    if project_obj.owner_name != user.name:
        await insert.project_user(project_uuid, user)


@router.post(
    "/project-org/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def add_project_org(
    project_uuid: str, organization: Organization, request: Request
):
    """Add an organization to a project.

    Args:
        project_uuid (str): UUID of the project to add the organizion to.
        organization (Organization): organization to be added to the project.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project_uuid, request)
    await insert.project_org(project_uuid, organization)


@router.post(
    "/copy-project/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def copy_project(
    project_uuid: str,
    copy_spec: ProjectCopy,
    request: Request,
    current_user=Depends(util.auth.claim()),
):
    """Create a copy of an existing project.

    Args:
        project_uuid (str): UUID of the project to be copied.
        copy_spec (ProjectCopy): specification of what content to copy over.
        request (Request): http request to get user information from.
        current_user (Any, optional): user initiating the copy request.
            Defaults to Depends(util.auth.claim()).
    """
    await util.project_access_valid(project_uuid, request)
    user = await select.user(current_user["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=("ERROR: User copying the project not found."),
        )
    await copy.project_copy(project_uuid, copy_spec, user)


@router.patch("/project/", tags=["zeno"], dependencies=[Depends(util.auth)])
async def update_project(project: Project, request: Request):
    """Update a project's specification.

    Args:
        project (Project): updated project specification.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project.uuid, request)
    await update.project(project)


@router.patch(
    "/project-user/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def update_project_user(project_uuid: str, user: User, request: Request):
    """Update the rights of a project user.

    Args:
        project_uuid (str): UUID of the project to update user rights for.
        user (User): updated user rights of a specified user.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project_uuid, request)
    await update.project_user(project_uuid, user)


@router.patch(
    "/project-org/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def update_project_org(
    project_uuid: str, organization: Organization, request: Request
):
    """Update the rights of a project's organization.

    Args:
        project_uuid (str): UUID of the project to update organization rights for.
        organization (Organization): updated rights of a specified organization.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project_uuid, request)
    await update.project_org(project_uuid, organization)


@router.delete("/project/{project_uuid}", tags=["zeno"])
async def delete_project(project_uuid: str, current_user=Depends(util.auth.claim())):
    """Delete a project from the database.

    Args:
        project_uuid (str): UUID of the project to be deleted.
        current_user (Any, optional): user sending the delete request.
            Defaults to Depends(util.auth.claim()).
    """
    project_obj = await select.project_from_uuid(project_uuid)
    if project_obj.owner_name != current_user["username"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=("ERROR: Only project owners can delete projects."),
        )
    data_path = Path("data", project_uuid)
    if data_path.exists():
        shutil.rmtree(data_path)
    await delete.project(project_uuid)


@router.delete(
    "/project-user/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def delete_project_user(project_uuid: str, user: User, request: Request):
    """Remove a user from a project.

    Args:
        project_uuid (str): UUID of the project to remove the user from.
        user (User): user to be removed from the project.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project_uuid, request)
    await delete.project_user(project_uuid, user)


@router.delete(
    "/project-org/{project_uuid}", tags=["zeno"], dependencies=[Depends(util.auth)]
)
async def delete_project_org(
    project_uuid: str, organization: Organization, request: Request
):
    """Remove an organization from a project.

    Args:
        project_uuid (str): UUID of the project to remove the organization from.
        organization (Organization): organization to be removed from the project.
        request (Request): http request to get user information from.
    """
    await util.project_editor(project_uuid, request)
    await delete.project_org(project_uuid, organization)
