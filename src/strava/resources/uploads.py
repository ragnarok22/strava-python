from __future__ import annotations

from typing import IO, Any

from strava._serialization import to_form_data
from strava._types import NOT_GIVEN, NotGiven
from strava.models.uploads import Upload
from strava.resources._base import AsyncAPIResource, SyncAPIResource


def _upload_create_data(
    *,
    name: str | NotGiven = NOT_GIVEN,
    description: str | NotGiven = NOT_GIVEN,
    trainer: bool | NotGiven = NOT_GIVEN,
    commute: bool | NotGiven = NOT_GIVEN,
    data_type: str | NotGiven = NOT_GIVEN,
    external_id: str | NotGiven = NOT_GIVEN,
) -> dict[str, Any]:
    return to_form_data(
        {
            "name": name,
            "description": description,
            "trainer": trainer,
            "commute": commute,
            "data_type": data_type,
            "external_id": external_id,
        }
    )


def _upload_files(file: IO[bytes] | bytes | None) -> dict[str, Any] | None:
    if file is None:
        return None
    if isinstance(file, bytes):
        return {"file": ("upload", file)}
    return {"file": file}


class Uploads(SyncAPIResource):
    def create(
        self,
        *,
        file: IO[bytes] | bytes | None = None,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
        data_type: str | NotGiven = NOT_GIVEN,
        external_id: str | NotGiven = NOT_GIVEN,
    ) -> Upload:
        data = _upload_create_data(
            name=name,
            description=description,
            trainer=trainer,
            commute=commute,
            data_type=data_type,
            external_id=external_id,
        )
        files = _upload_files(file)
        return self._client._request_model(
            "POST", "/uploads", data=data, files=files, model_cls=Upload
        )

    def retrieve(self, upload_id: int) -> Upload:
        return self._client._request_model(
            "GET", f"/uploads/{upload_id}", model_cls=Upload
        )


class AsyncUploads(AsyncAPIResource):
    async def create(
        self,
        *,
        file: IO[bytes] | bytes | None = None,
        name: str | NotGiven = NOT_GIVEN,
        description: str | NotGiven = NOT_GIVEN,
        trainer: bool | NotGiven = NOT_GIVEN,
        commute: bool | NotGiven = NOT_GIVEN,
        data_type: str | NotGiven = NOT_GIVEN,
        external_id: str | NotGiven = NOT_GIVEN,
    ) -> Upload:
        data = _upload_create_data(
            name=name,
            description=description,
            trainer=trainer,
            commute=commute,
            data_type=data_type,
            external_id=external_id,
        )
        files = _upload_files(file)
        return await self._client._request_model(
            "POST", "/uploads", data=data, files=files, model_cls=Upload
        )

    async def retrieve(self, upload_id: int) -> Upload:
        return await self._client._request_model(
            "GET", f"/uploads/{upload_id}", model_cls=Upload
        )
