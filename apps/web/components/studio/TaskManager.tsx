"use client";

import { useEffect, useState } from "react";
import { isCustom, SCENARIOS, studio, type StudioTask } from "@/lib/studio";
import { TaskEditor } from "./TaskEditor";

function describeCheck(task: StudioTask): string {
  const { url_prefix, text_present, answer_contains } = task.success;
  if (url_prefix) return `reaches a page starting with ${url_prefix}`;
  if (text_present) return `the page shows “${text_present}”`;
  return `the answer contains ${answer_contains.map((word) => `“${word}”`).join(" and ")}`;
}

/** A site's tasks: built-in ones are listed, custom ones can be added, edited and deleted. */
export function TaskManager({ siteId }: { siteId: string }) {
  const [tasks, setTasks] = useState<StudioTask[] | null>(null);
  const [editing, setEditing] = useState<string | null>(null); // a task id, or "new"
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    studio
      .siteTasks(siteId)
      .then(setTasks)
      .catch((problem: Error) => setError(problem.message));
  }, [siteId]);

  function saved(task: StudioTask) {
    setTasks((current) => {
      const list = current ?? [];
      return list.some((item) => item.id === task.id)
        ? list.map((item) => (item.id === task.id ? task : item))
        : [...list, task];
    });
    setNotice(editing === "new" ? "The task was added." : "The task was saved.");
    setEditing(null);
  }

  async function remove(task: StudioTask) {
    try {
      await studio.deleteTask(task.id);
      setTasks((current) => current?.filter((item) => item.id !== task.id) ?? null);
      setNotice("The task was deleted.");
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : "The task could not be deleted.");
    }
  }

  if (error) return <p role="alert" className="pixel-panel text-rose">{error}</p>;
  if (!tasks) return <p className="text-mist">Loading tasks…</p>;

  return (
    <section aria-labelledby="tasks-title" className="grid gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="tasks-title" className="font-display text-3xl font-bold text-amber">
          Tasks
        </h2>
        {editing === null ? (
          <button
            type="button"
            className="pixel-button"
            onClick={() => {
              setNotice("");
              setEditing("new");
            }}
          >
            Add a task
          </button>
        ) : null}
      </div>
      <p role="status" className="text-moss">
        {notice}
      </p>
      {editing === "new" ? (
        <TaskEditor siteId={siteId} onSaved={saved} onCancel={() => setEditing(null)} />
      ) : null}
      {tasks.length ? (
        <ul className="grid gap-4">
          {tasks.map((task) =>
            editing === task.id ? (
              <li key={task.id}>
                <TaskEditor siteId={siteId} task={task} onSaved={saved} onCancel={() => setEditing(null)} />
              </li>
            ) : (
              <li key={task.id} className={`pixel-panel grid gap-2 ${isCustom(task.id) ? "lit" : ""}`}>
                <p className="text-lg text-parchment">{task.instruction}</p>
                <p className="text-sm text-mist">
                  {SCENARIOS.find((option) => option.id === task.scenario)?.name ?? "No kind given"} ·
                  starts at <code>{task.start_path}</code> · done when {describeCheck(task)}
                </p>
                <p className="text-sm text-mist">
                  {isCustom(task.id) ? "Your task" : "Built-in task, read-only"} ·{" "}
                  <code className="text-xs">{task.id}</code>
                </p>
                {isCustom(task.id) ? (
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      className="pixel-button quiet"
                      onClick={() => {
                        setNotice("");
                        setEditing(task.id);
                      }}
                    >
                      Edit
                    </button>
                    <button type="button" className="pixel-button quiet" onClick={() => remove(task)}>
                      Delete
                    </button>
                  </div>
                ) : null}
              </li>
            ),
          )}
        </ul>
      ) : (
        <p className="pixel-panel text-mist">
          No tasks yet. Add one so that simulated users have something to do on this site.
        </p>
      )}
    </section>
  );
}
