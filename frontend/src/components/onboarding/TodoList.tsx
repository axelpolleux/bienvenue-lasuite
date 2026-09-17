import type { TodoWithStatus } from "../../types";
import { TodoItemRow } from "./TodoItemRow";

export interface TodoListProps {
  todos: TodoWithStatus[];
  busyTodoId: string | null;
  onVerify: (todoId: string) => void;
  onToggle: (todoId: string, next: boolean) => void;
  onOpenSignature: () => void;
}

/** Renders every checklist step in order; see `03-frontend-app.md` section 5 for the locking rule. */
export function TodoList({ todos, busyTodoId, onVerify, onToggle, onOpenSignature }: TodoListProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {todos.map((todo) => (
        <TodoItemRow
          key={todo.id}
          todo={todo}
          busy={busyTodoId === todo.id}
          onVerify={() => onVerify(todo.id)}
          onToggle={(next) => onToggle(todo.id, next)}
          onOpenSignature={onOpenSignature}
        />
      ))}
    </div>
  );
}
