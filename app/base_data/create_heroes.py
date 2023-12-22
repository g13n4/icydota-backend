from sqlmodel import select

from app.models import Hero


async def create_heroes(db_session, web_client, update_heroes: bool = False) -> None:
    sel_result = await db_session.execute(select(Hero))
    db_heroes = sel_result.scalars().all()
    if db_heroes and not update_heroes:
        return

    heroes_db_dict = {x.odota_id: x for x in db_heroes}
    r = await web_client.get('https://api.opendota.com/api/heroes')
    heroes = r.json()
    for hero in heroes:
        if hero['id'] in heroes_db_dict:
            pass

        new_hero = Hero(
            odota_id=hero['id'],
            name=hero['localized_name'],
            npc_name=hero['name']
        )
        await db_session.add(new_hero)

    await db_session.commit()
