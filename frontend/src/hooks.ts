import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, ApiError, type BookFilter, type BookInput } from "./api";

const ERROR_TITLES: Record<number, string> = {
  0: "Sin conexión",
  400: "Datos inválidos",
  404: "No encontrado",
  500: "Error del servidor",
  503: "Servicio no disponible",
};

export function notifyError(error: Error) {
  const status = error instanceof ApiError ? error.status : -1;
  toast.error(ERROR_TITLES[status] ?? "Error inesperado", { description: error.message });
}

export function useBooks(filter: BookFilter, page: number) {
  return useQuery({
    queryKey: ["books", filter, page],
    queryFn: () => api.listBooks(filter, page),
    placeholderData: keepPreviousData,
  });
}

export function useBook(id: number | null) {
  return useQuery({
    queryKey: ["book", id],
    queryFn: () => api.getBook(id as number),
    enabled: id !== null,
  });
}

function useApiMutation<TVars, TData>(mutationFn: (vars: TVars) => Promise<TData>, successMessage: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => {
      toast.success(successMessage);
      void queryClient.invalidateQueries();
    },
  });
}

export const useSaveBook = () =>
  useApiMutation(
    ({ id, data }: { id: number | null; data: BookInput }) =>
      id === null ? api.createBook(data) : api.updateBook(id, data),
    "Libro guardado",
  );

export const useDeleteBook = () => useApiMutation(api.deleteBook, "Libro eliminado");

export const useCalculatePrice = () => useApiMutation(api.calculatePrice, "Precio de venta calculado");
