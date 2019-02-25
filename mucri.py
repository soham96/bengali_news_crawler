import asyncio
import aiohttp


async def _fetch_link(action, url, data, headers, resp_type):
    async with aiohttp.ClientSession() as session:
        if action == "get":
            resp = await session.get(url)
        elif action == "post":
            resp = await session.post(url, data=data, headers=headers)

        if resp_type == "html":
            return await resp.read()
        elif resp_type == "json":
            return await resp.json()
        return None


def fetch_pages(links=None):
    if not links:
        print("No links provided to fetch")
        return

    tasks = []
    fetched_data = []
    loop = asyncio.get_event_loop()

    for link in links:
        if isinstance(link, str):
            url = link
            action = "get"
            data = {}
            headers = {}
            resp_type = "html"
        elif isinstance(link, dict):
            action = link.get("action", "get")
            url = link["url"]
            data = link.get("data", {})
            headers = link.get("headers", {})
            resp_type = link.get("resp_type", "text")

        tasks.append(
            asyncio.ensure_future(_fetch_link(action, url, data, headers, resp_type))
        )

    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        fetched_data.append(task.result())
    return fetched_data


if __name__ == "__main__":
    links = [
        "http://meain.github.io",
        {"url": "https://google.com"},
        {"url": "http://github.com"},
    ]
    result = fetch_pages(links)
    print(len(result))