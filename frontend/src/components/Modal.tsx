import { useEffect, useRef, type ReactNode } from "react";

interface Props {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}

// <dialog> nativo: showModal() da el fondo, atrapa el foco y cierra con Esc.
export function Modal({ open, title, onClose, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (open && !dialog?.open) dialog?.showModal();
    if (!open && dialog?.open) dialog.close();
  }, [open]);

  return (
    <dialog ref={ref} onClose={onClose}>
      <article>
        <header>
          <a
            href="#close"
            aria-label="Cerrar"
            rel="prev"
            onClick={(e) => {
              e.preventDefault();
              onClose();
            }}
          />
          <h3>{title}</h3>
        </header>
        {/* Los hijos se montan solo mientras está abierto: cada apertura empieza de cero. */}
        {open && children}
      </article>
    </dialog>
  );
}
