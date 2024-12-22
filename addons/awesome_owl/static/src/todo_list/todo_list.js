import { Component, useState , onRendered} from '@odoo/owl';
import { TodoItem } from './todo_item';
import { useAutofocus } from "../utils";

export class TodoList extends Component {
    static template = 'awesome_owl.TodoList';
    static components = { TodoItem };

    setup() {
        // this.todos = useState([
        //     { id: 2, description: "write tutorial", isCompleted:true },
        //     { id: 3, description: "buy milk", isCompleted:false},
        // ]);
        this.nextId = 0;
        this.todos = useState([]);
        useAutofocus("input");
        onRendered(() => {
            console.log('TodoList has been rendered or updated!');
            const todoCount = this.todos.length;
            console.log(`Current number of todos: ${todoCount}`);
        });
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value != "") {
            this.todos.push({
                id: this.nextId++,
                description: ev.target.value,
                isCompleted: false
            });
            ev.target.value = "";
        }
    }

    toggleTodo(todoId) {
        const todo = this.todos.find((todo) => todo.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    removeTodo(todoId) {
        const todoIndex = this.todos.findIndex((todo) => todo.id === todoId);
        if (todoIndex >= 0) {
            this.todos.splice(todoIndex, 1);
        }
    }
}