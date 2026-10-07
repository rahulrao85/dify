"""SQLite-backed tests for summary index handling when duplicate documents are re-indexed."""

from __future__ import annotations

import uuid
from functools import partial
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

import tasks.duplicate_document_indexing_task as task_module
from core.rag.index_processor.constant.index_type import IndexStructureType, IndexTechniqueType
from models.dataset import Dataset, Document, DocumentSegment
from models.enums import DataSourceType, DocumentCreatedFrom, IndexingStatus
from tasks.duplicate_document_indexing_task import _duplicate_document_indexing_task


@pytest.fixture
def task_harness(
    sqlite_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[MagicMock, MagicMock]:
    """Bind task-owned sessions to SQLite and keep only external boundaries mocked."""
    engine = sqlite_session.get_bind()
    monkeypatch.setattr(
        task_module.session_factory,
        "create_session",
        lambda: Session(engine, expire_on_commit=False),
    )
    runner = MagicMock()
    processor = MagicMock()
    monkeypatch.setattr(task_module, "build_document_indexing_service", MagicMock(return_value=runner))
    monkeypatch.setattr(
        task_module,
        "IndexProcessorFactory",
        MagicMock(return_value=MagicMock(init_index_processor=MagicMock(return_value=processor))),
    )
    return runner, processor


def _persist_rows(
    session: Session,
    *,
    indexing_technique: IndexTechniqueType = IndexTechniqueType.HIGH_QUALITY,
    summary_index_setting: dict | None = None,
    doc_form: IndexStructureType = IndexStructureType.PARAGRAPH_INDEX,
    need_summary: bool = True,
) -> tuple[Dataset, Document]:
    tenant_id = str(uuid.uuid4())
    dataset_id = str(uuid.uuid4())
    document_id = str(uuid.uuid4())
    created_by = str(uuid.uuid4())
    dataset = Dataset(
        id=dataset_id,
        tenant_id=tenant_id,
        name="Duplicate dataset",
        data_source_type=DataSourceType.UPLOAD_FILE,
        created_by=created_by,
        indexing_technique=indexing_technique,
        summary_index_setting=summary_index_setting,
    )
    document = Document(
        id=document_id,
        tenant_id=tenant_id,
        dataset_id=dataset_id,
        position=1,
        data_source_type=DataSourceType.UPLOAD_FILE,
        batch="batch-1",
        name="document.txt",
        created_from=DocumentCreatedFrom.WEB,
        created_by=created_by,
        indexing_status=IndexingStatus.WAITING,
        doc_form=doc_form,
        need_summary=need_summary,
    )
    segment = DocumentSegment(
        tenant_id=tenant_id,
        dataset_id=dataset_id,
        document_id=document_id,
        position=1,
        content="segment",
        word_count=1,
        tokens=1,
        created_by=created_by,
        index_node_id="node-1",
    )
    session.add_all([dataset, document, segment])
    session.commit()
    return dataset, document


def _complete_indexing(refs, *, bind) -> None:
    with Session(bind) as writer, writer.begin():
        for ref in refs:
            writer.get(Document, ref.document_id).indexing_status = IndexingStatus.COMPLETED


def test_deletes_old_summaries_when_cleaning_duplicate_document(
    sqlite_session: Session,
    task_harness: tuple[MagicMock, MagicMock],
) -> None:
    _runner, processor = task_harness
    dataset, document = _persist_rows(sqlite_session, summary_index_setting={"enable": True})

    _duplicate_document_indexing_task(dataset.id, [document.id])

    processor.clean.assert_called_once()
    _dataset_arg, node_ids = processor.clean.call_args.args
    assert node_ids == ["node-1"]
    assert processor.clean.call_args.kwargs["delete_summaries"] is True


def test_queues_summary_when_duplicate_reindex_completes(
    sqlite_session: Session,
    task_harness: tuple[MagicMock, MagicMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner, _processor = task_harness
    dataset, document = _persist_rows(sqlite_session, summary_index_setting={"enable": True})
    runner.run.side_effect = partial(_complete_indexing, bind=sqlite_session.get_bind())
    delay = MagicMock()
    monkeypatch.setattr(task_module.generate_summary_index_task, "delay", delay)

    _duplicate_document_indexing_task(dataset.id, [document.id])

    delay.assert_called_once_with(dataset.id, document.id, None)


@pytest.mark.parametrize(
    ("dataset_changes", "document_changes"),
    [
        ({"indexing_technique": IndexTechniqueType.ECONOMY}, {}),
        ({"summary_index_setting": None}, {}),
        ({"summary_index_setting": {"enable": False}}, {}),
        ({}, {"need_summary": False}),
        ({}, {"doc_form": IndexStructureType.QA_INDEX}),
    ],
)
def test_skips_summary_when_persisted_eligibility_does_not_match(
    sqlite_session: Session,
    task_harness: tuple[MagicMock, MagicMock],
    monkeypatch: pytest.MonkeyPatch,
    dataset_changes: dict,
    document_changes: dict,
) -> None:
    runner, _processor = task_harness
    dataset, document = _persist_rows(sqlite_session, summary_index_setting={"enable": True})
    for key, value in dataset_changes.items():
        setattr(dataset, key, value)
    for key, value in document_changes.items():
        setattr(document, key, value)
    sqlite_session.commit()
    runner.run.side_effect = partial(_complete_indexing, bind=sqlite_session.get_bind())
    delay = MagicMock()
    monkeypatch.setattr(task_module.generate_summary_index_task, "delay", delay)

    _duplicate_document_indexing_task(dataset.id, [document.id])

    delay.assert_not_called()


def test_skips_summary_when_duplicate_reindex_fails(
    sqlite_session: Session,
    task_harness: tuple[MagicMock, MagicMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner, _processor = task_harness
    dataset, document = _persist_rows(sqlite_session, summary_index_setting={"enable": True})
    runner.run.side_effect = RuntimeError("indexing failed")
    delay = MagicMock()
    monkeypatch.setattr(task_module.generate_summary_index_task, "delay", delay)

    _duplicate_document_indexing_task(dataset.id, [document.id])

    delay.assert_not_called()
