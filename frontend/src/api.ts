const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const PAGE_SIZE = 10;
export const LOW_STOCK_THRESHOLD = 10;

export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  cost_usd: number;
  selling_price_local: number | null;
  stock_quantity: number;
  category: string;
  supplier_country: string;
  created_at: string;
  updated_at: string;
}

export type BookInput = Omit<Book, "id" | "selling_price_local" | "created_at" | "updated_at">;

export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface PriceCalculation {
  book_id: number;
  cost_usd: number;
  exchange_rate: number;
  cost_local: number;
  margin_percentage: number;
  selling_price_local: number;
  currency: "VES";
  rate_source: "live" | "default";
  calculation_timestamp: string;
}

export type BookFilter =
  | { kind: "all" }
  | { kind: "category"; category: string }
  | { kind: "lowStock"; threshold: number };

function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === "object") {
    if ("detail" in body) return String(body.detail);
    // Errores de validación de DRF: { campo: ["mensaje", ...] }
    return Object.entries(body)
      .map(([field, messages]) => `${field}: ${[messages].flat().join(" ")}`)
      .join(" · ");
  }
  return `Error ${status}`;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super(errorMessage(status, body));
    this.status = status;
    this.body = body;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError(0, { detail: "No se pudo conectar con la API." });
  }
  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, body);
  return body as T;
}

export const api = {
  listBooks(filter: BookFilter, page: number) {
    const params = new URLSearchParams({ page: String(page) });
    let path = "/books";
    if (filter.kind === "category") {
      path = "/books/search";
      params.set("category", filter.category);
    } else if (filter.kind === "lowStock") {
      path = "/books/low-stock";
      params.set("threshold", String(filter.threshold));
    }
    return request<Page<Book>>(`${path}?${params}`);
  },
  getBook: (id: number) => request<Book>(`/books/${id}`),
  createBook: (data: BookInput) =>
    request<Book>("/books", { method: "POST", body: JSON.stringify(data) }),
  updateBook: (id: number, data: BookInput) =>
    request<Book>(`/books/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteBook: (id: number) => request<null>(`/books/${id}`, { method: "DELETE" }),
  calculatePrice: (id: number) =>
    request<PriceCalculation>(`/books/${id}/calculate-price`, { method: "POST" }),
};
