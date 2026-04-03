import json
import re
import anthropic
from config import claude_api_key


def classify_tasks_with_ai(tasks: list[dict], categories: list[dict]) -> dict[int, int | None]:
    """
    Ask Claude to assign each task to the best matching category.

    Args:
        tasks: list of {id, title, description}
        categories: list of {id, name}

    Returns:
        dict mapping task_id -> category_id (or None if no good match)
    """
    if not claude_api_key or not categories or not tasks:
        return {}

    categories_text = "\n".join(f"  ID={c['id']}: {c['name']}" for c in categories)

    tasks_text = "\n".join(
        f"  ID={t['id']}: {t['title']}" + (f" — {t['description']}" if t.get("description") else "")
        for t in tasks
    )

    prompt = f"""Eres un asistente de clasificación de tareas para una empresa agrícola llamada IMPAG.

CATEGORÍAS DISPONIBLES:
{categories_text}

TAREAS A CLASIFICAR:
{tasks_text}

Para cada tarea, asigna la categoría que mejor se ajuste según el contenido (facturación, cotizaciones, pedidos, entregas, pagos, etc.).
Si ninguna categoría aplica, usa null.

Devuelve ÚNICAMENTE un JSON array, sin texto adicional, con objetos así:
[{{"task_id": 1, "category_id": 3}}, {{"task_id": 2, "category_id": null}}, ...]

Incluye una entrada por cada tarea en el mismo orden. Usa los IDs exactos de las categorías."""

    client = anthropic.Anthropic(api_key=claude_api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if response_text.startswith("```"):
        response_text = re.sub(r"^```(?:json)?\n?", "", response_text)
        response_text = re.sub(r"\n?```$", "", response_text)

    try:
        results = json.loads(response_text)
    except json.JSONDecodeError:
        return {}

    valid_category_ids = {c["id"] for c in categories}
    assignments: dict[int, int | None] = {}
    for item in results:
        task_id = item.get("task_id")
        cat_id = item.get("category_id")
        if task_id is None:
            continue
        # Only accept valid category IDs
        if cat_id is not None and cat_id not in valid_category_ids:
            cat_id = None
        assignments[task_id] = cat_id

    return assignments
