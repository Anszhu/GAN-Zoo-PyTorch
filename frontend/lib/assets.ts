const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export function resolveAssetUrl(url: string) {
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  const backendBase = apiUrl.replace(/\/api\/v1$/, "");
  return `${backendBase}${url.startsWith("/") ? url : `/${url}`}`;
}

