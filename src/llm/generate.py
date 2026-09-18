import json

from pydantic import BaseModel

from .client import DEFAULT_MODEL


def generate_parsed(
    client,
    prompt: str,
    schema: type[BaseModel],
    temperature: float,
    fallback_system: str,
) -> BaseModel:
    try:
        completion = client.beta.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format=schema,
            temperature=temperature,
            max_tokens=500,
        )
        data = completion.choices[0].message.parsed
        if not data:
            raise ValueError("Parsed output returned None.")
        return data
    except Exception:  # noqa: BLE001
        raw_res = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": fallback_system},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        content_str = raw_res.choices[0].message.content or "{}"
        return schema(**json.loads(content_str))