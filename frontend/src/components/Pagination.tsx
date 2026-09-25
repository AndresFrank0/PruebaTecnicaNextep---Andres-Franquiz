import { PAGE_SIZE } from "../api";

interface Props {
  page: number;
  count: number;
  onPage: (page: number) => void;
}

export function Pagination({ page, count, onPage }: Props) {
  const pages = Math.max(1, Math.ceil(count / PAGE_SIZE));
  return (
    <nav>
      <ul>
        <li><small>{count} libros · Página {page} de {pages}</small></li>
      </ul>
      <ul>
        <li><button className="outline" disabled={page <= 1} onClick={() => onPage(page - 1)}>Anterior</button></li>
        <li><button className="outline" disabled={page >= pages} onClick={() => onPage(page + 1)}>Siguiente</button></li>
      </ul>
    </nav>
  );
}
