const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function fetcher(url: string) {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}

export async function fetchFeed(
  tags?: string[],
  lane?: string,
  range: number = 7,
  page: number = 1,
) {
  const params = new URLSearchParams();
  params.append("range", range.toString());
  params.append("page", page.toString());

  if (lane) params.append("lane", lane);
  if (tags && tags.length > 0) {
    tags.forEach((t) => params.append("tag", t));
  }

  return fetcher(`/api/feed?${params.toString()}`);
}

export async function fetchItemDetail(id: string) {
  return fetcher(`/api/items/${id}`);
}

export async function fetchTags() {
  return fetcher("/api/tags");
}

export async function toggleBookmark(id: string, currentlyBookmarked: boolean) {
  const method = currentlyBookmarked ? "DELETE" : "POST";
  const res = await fetch(`${API_BASE}/api/items/${id}/bookmark`, { method });
  if (!res.ok) throw new Error("Bookmark toggle failed");
  return res.json();
}

export async function markAsRead(id: string) {
  const res = await fetch(`${API_BASE}/api/items/${id}/read`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Mark read failed");
  return res.json();
}

export async function hideItem(id: string) {
  const res = await fetch(`${API_BASE}/api/items/${id}/hide`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Hide item failed");
  return res.json();
}

export async function triggerIngestion() {
  const res = await fetch(`${API_BASE}/api/ingest/run`, { method: "POST" });
  if (!res.ok) throw new Error("Run ingestion failed");
  return res.json();
}

export async function getIngestionStatus() {
  return fetcher("/api/ingest/status");
}
