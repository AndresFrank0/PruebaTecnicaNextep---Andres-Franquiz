import { useState } from "react";
import { LOW_STOCK_THRESHOLD, type BookFilter } from "../api";

interface Props {
  filter: BookFilter;
  onChange: (filter: BookFilter) => void;
}

export function Filters({ filter, onChange }: Props) {
  const [category, setCategory] = useState("");
  const [threshold, setThreshold] = useState(LOW_STOCK_THRESHOLD);

  return (
    <article>
      <div className="grid">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const value = category.trim();
            onChange(value ? { kind: "category", category: value } : { kind: "all" });
          }}
        >
          <fieldset role="group">
            <input
              type="search"
              placeholder="Buscar por categoría"
              aria-label="Categoría"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <button type="submit">Buscar</button>
          </fieldset>
        </form>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onChange({ kind: "lowStock", threshold });
          }}
        >
          <fieldset role="group">
            <input
              type="number"
              min={0}
              aria-label="Umbral de stock bajo"
              value={threshold}
              onChange={(e) => setThreshold(e.target.valueAsNumber || 0)}
            />
            <button type="submit" className="secondary">Ver stock bajo</button>
          </fieldset>
        </form>
      </div>
      {filter.kind !== "all" && (
        <button
          className="outline"
          onClick={() => {
            setCategory("");
            onChange({ kind: "all" });
          }}
        >
          Limpiar filtros
        </button>
      )}
    </article>
  );
}
