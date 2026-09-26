import { LOW_STOCK_THRESHOLD, type Book } from "../api";
import { formatBs, formatUsd } from "../format";

interface Props {
  books: Book[];
  onDetail: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (book: Book) => void;
}

export function BookTable({ books, onDetail, onEdit, onDelete }: Props) {
  if (books.length === 0) return <p>No hay libros para mostrar.</p>;

  return (
    <div className="overflow-auto">
      <table className="striped">
        <thead>
          <tr>
            <th>Título</th>
            <th>Autor</th>
            <th>ISBN</th>
            <th>Categoría</th>
            <th>Stock</th>
            <th>Costo (USD)</th>
            <th>Precio venta (Bs.)</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {books.map((book) => (
            <tr key={book.id}>
              <td>{book.title}</td>
              <td>{book.author}</td>
              <td>{book.isbn}</td>
              <td>{book.category}</td>
              <td>
                {book.stock_quantity <= LOW_STOCK_THRESHOLD ? <mark>{book.stock_quantity}</mark> : book.stock_quantity}
              </td>
              <td>{formatUsd(book.cost_usd)}</td>
              <td>{book.selling_price_local === null ? "—" : formatBs(book.selling_price_local)}</td>
              <td>
                <div role="group">
                  <button onClick={() => onDetail(book.id)}>Detalle / Precio</button>
                  <button className="secondary" onClick={() => onEdit(book.id)}>Editar</button>
                  <button className="contrast" onClick={() => onDelete(book)}>Eliminar</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
