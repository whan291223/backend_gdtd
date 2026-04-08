from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from model.models import LabCategory, LabField, LabRecord, LabValue
from schema.lab_schema import LabCategoryUpdate, LabRecordCreate
from typing import List
from datetime import datetime, timezone


async def get_lab_config(session: AsyncSession) -> List[LabCategory]:
    result = await session.execute(
        select(LabCategory)
        .options(selectinload(LabCategory.fields))
        .order_by(LabCategory.display_order)
    )
    return result.scalars().all()


async def update_lab_config(session: AsyncSession, categories_data: List[LabCategoryUpdate]):
    # Get existing categories
    existing_categories_result = await session.execute(select(LabCategory))
    existing_categories = {c.id: c for c in existing_categories_result.scalars().all()}

    incoming_category_ids = {c.id for c in categories_data if c.id}

    # Delete categories not in incoming data
    for cat_id in list(existing_categories.keys()):
        if cat_id not in incoming_category_ids:
            await session.delete(existing_categories[cat_id])

    for cat_data in categories_data:
        if cat_data.id and cat_data.id in existing_categories:
            # Update existing category
            category = existing_categories[cat_data.id]
            category.name = cat_data.name
            category.display_order = cat_data.display_order
            category.updated_at = datetime.now(timezone.utc)

            # Handle fields
            existing_fields_result = await session.execute(
                select(LabField).where(LabField.category_id == category.id)
            )
            existing_fields = {f.id: f for f in existing_fields_result.scalars().all()}
            incoming_field_ids = {f.id for f in cat_data.fields if f.id}

            # Delete fields not in incoming data
            for field_id in list(existing_fields.keys()):
                if field_id not in incoming_field_ids:
                    await session.delete(existing_fields[field_id])

            for field_data in cat_data.fields:
                if field_data.id and field_data.id in existing_fields:
                    # Update field
                    field = existing_fields[field_data.id]
                    field.name = field_data.name
                    field.unit = field_data.unit
                    field.display_order = field_data.display_order
                else:
                    # New field in existing category
                    new_field = LabField(
                        category_id=category.id,
                        name=field_data.name,
                        unit=field_data.unit,
                        display_order=field_data.display_order
                    )
                    session.add(new_field)
        else:
            # New category
            new_category = LabCategory(
                name=cat_data.name,
                display_order=cat_data.display_order
            )
            session.add(new_category)
            await session.flush()  # To get new_category.id

            for field_data in cat_data.fields:
                new_field = LabField(
                    category_id=new_category.id,
                    name=field_data.name,
                    unit=field_data.unit,
                    display_order=field_data.display_order
                )
                session.add(new_field)

    await session.commit()


async def create_lab_record(session: AsyncSession, user_id: int, data: LabRecordCreate) -> LabRecord:
    record = LabRecord(user_id=user_id, note=data.note)
    session.add(record)
    await session.flush()

    for val in data.values:
        lab_value = LabValue(
            record_id=record.id,
            field_id=val.field_id,
            value=val.value
        )
        session.add(lab_value)

    await session.commit()
    await session.refresh(record)
    return record


async def delete_lab_record(session: AsyncSession, lab_record_id: int):
    result = await session.execute(select(LabRecord).where(LabRecord.id == lab_record_id))
    record = result.scalar_one_or_none()
    if record:
        await session.delete(record)
        await session.commit()
        return True
    return False


async def get_lab_history(session: AsyncSession, user_id: int) -> List[LabRecord]:
    result = await session.execute(
        select(LabRecord)
        .options(selectinload(LabRecord.values))
        .where(LabRecord.user_id == user_id)
        .order_by(LabRecord.recorded_at.desc())
    )
    return result.scalars().all()
