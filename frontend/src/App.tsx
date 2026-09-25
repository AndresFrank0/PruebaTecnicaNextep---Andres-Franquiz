import { useState } from "react";
import type { Book, BookFilter } from "./api";
import { BookDetail } from "./components/BookDetail";
import { BookForm } from "./components/BookForm";
import { BookTable } from "./components/BookTable";
import { ConfirmDialog } from "./components/ConfirmDialog";
import { Filters } from "./components/Filters";
import { Modal } from "./components/Modal";
import { Pagination } from "./components/Pagination";
import { useBooks, useDeleteBook } from "./hooks";

export default function App() {
  const [filter, setFilter] = useState<BookFilter>({ kind: "all" });
  const [page, setPage] = useState(1);
  const [formId, setFormId] = useState<number | "new" | null>(null);
  const [detailId, setDetailId] = useState<number | null>(null);
  const [toDelete, setToDelete] = useState<Book | null>(null);

  const books = useBooks(filter, page);
  const deleteBook = useDeleteBook();

  function changeFilter(next: BookFilter) {
    setFilter(next);
    setPage(1);
  }

  function confirmDelete() {
    if (!toDelete) return;
    deleteBook.mutate(toDelete.id, {
      onSuccess: () => {
        // Si se borra la última fila de una página, esa página deja de existir (DRF respondería 404).
        if (books.data?.results.length === 1 && page > 1) setPage(page - 1);
        setToDelete(null);
      },
    });
  }

  return (
    <main className="container">
      <nav>
        <ul><li><h1>Inventario de Librería</h1></li></ul>
        <ul><li><button onClick={() => setFormId("new")}>+ Nuevo libro</button></li></ul>
      </nav>

      <Filters filter={filter} onChange={changeFilter} />

      {books.isError ? (
        <p>
          No se pudieron cargar los libros.{" "}
          <button className="outline" onClick={() => books.refetch()}>Reintentar</button>
        </p>
      ) : !books.data ? (
        <p aria-busy="true">Cargando libros…</p>
      ) : (
        <>
          {books.isFetching && <progress />}
          <BookTable books={books.data.results} onDetail={setDetailId} onEdit={setFormId} onDelete={setToDelete} />
          <Pagination page={page} count={books.data.count} onPage={setPage} />
        </>
      )}

      <Modal open={formId !== null} title={formId === "new" ? "Nuevo libro" : "Editar libro"} onClose={() => setFormId(null)}>
        <BookForm bookId={formId === "new" ? null : formId} onDone={() => setFormId(null)} />
      </Modal>

      <Modal open={detailId !== null} title="Detalle del libro" onClose={() => setDetailId(null)}>
        {detailId !== null && <BookDetail bookId={detailId} />}
      </Modal>

      <ConfirmDialog
        open={toDelete !== null}
        title="Eliminar libro"
        message={`¿Seguro que deseas eliminar «${toDelete?.title}»? Esta acción no se puede deshacer.`}
        confirmLabel="Eliminar"
        busy={deleteBook.isPending}
        onCancel={() => setToDelete(null)}
        onConfirm={confirmDelete}
      />
    </main>
  );
}
