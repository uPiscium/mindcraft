export class TaskPool {
    constructor(tasks = []) {
        this.tasks = tasks.map((task, index) => this._normalizeTask(task, index));
        this.currentTaskId = null;
        this.currentTaskDriving = false;
    }

    _normalizeTask(task, index) {
        const id = task.id ?? task.task_id ?? `task_${index}`;
        return {
            ...task,
            id,
            task_id: task.task_id ?? id,
            goal: task.goal ?? task.payload ?? null,
            payload: task.payload ?? task.goal ?? null,
            depends_on: Array.isArray(task.depends_on) ? [...task.depends_on] : [],
            priority: Number.isFinite(task.priority) ? task.priority : index,
            state: task.state ?? 'AVAILABLE',
            lock_metadata: task.lock_metadata ?? null,
            history: Array.isArray(task.history) ? [...task.history] : [],
        };
    }

    _getTask(taskId) {
        return this.tasks.find((task) => task.id === taskId) || null;
    }

    _dependenciesComplete(task) {
        return task.depends_on.every((dependencyId) => {
            const dependency = this._getTask(dependencyId);
            return dependency && dependency.state === 'COMPLETED';
        });
    }

    _availableTasks() {
        return this.tasks
            .filter((task) => task.state === 'AVAILABLE' && this._dependenciesComplete(task))
            .sort((left, right) => left.priority - right.priority || left.id.localeCompare(right.id));
    }

    hasAvailableTask() {
        return this._availableTasks().length > 0;
    }

    acquireNextTask() {
        const task = this._availableTasks()[0] || null;
        if (!task) {
            this.currentTaskId = null;
            this.currentTaskDriving = false;
            return null;
        }

        task.state = 'LOCKED';
        task.lock_metadata = {
            requester_id: 'agent',
            locked_at: Date.now(),
        };
        this.currentTaskId = task.id;
        this.currentTaskDriving = true;
        return this._serialize(task);
    }

    completeCurrentTask(reason) {
        const task = this.getCurrentTask();
        if (!task) return null;

        task.history.push({
            reason,
            recorded_at: Date.now(),
        });
        task.state = 'COMPLETED';
        task.lock_metadata = null;
        this.currentTaskId = null;
        this.currentTaskDriving = false;
        return this._serialize(task);
    }

    yieldCurrentTask(reason) {
        const task = this.getCurrentTask();
        if (!task) return null;

        task.history.push({
            reason,
            recorded_at: Date.now(),
        });
        task.state = 'AVAILABLE';
        task.lock_metadata = null;
        this.currentTaskId = null;
        this.currentTaskDriving = false;
        return this._serialize(task);
    }

    isDrivingTask() {
        return this.currentTaskDriving && this.currentTaskId !== null;
    }

    getCurrentTask() {
        if (!this.currentTaskId) return null;
        return this._getTask(this.currentTaskId);
    }

    getCurrentTaskData() {
        const task = this.getCurrentTask();
        return task ? this._serialize(task) : null;
    }

    setCurrentTaskContext(task) {
        if (!task) {
            this.currentTaskId = null;
            return null;
        }

        const current = this._getTask(task.id);
        if (!current) return null;
        this.currentTaskId = current.id;
        return this._serialize(current);
    }

    getCurrentTaskState() {
        const task = this.getCurrentTask();
        return task ? task.state : null;
    }

    getAllTasks() {
        return this.tasks.map((task) => this._serialize(task));
    }

    setTasks(tasks = []) {
        this.tasks = tasks.map((task, index) => this._normalizeTask(task, index));
        this.currentTaskId = null;
        this.currentTaskDriving = false;
        return this.getAllTasks();
    }

    _serialize(task) {
        return {
            ...task,
            depends_on: [...task.depends_on],
            history: [...task.history],
            lock_metadata: task.lock_metadata ? { ...task.lock_metadata } : null,
        };
    }
}
