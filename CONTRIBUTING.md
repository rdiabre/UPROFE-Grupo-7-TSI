# Guía de contribución — UPROFE

Este documento resume cómo trabajamos los 8 integrantes del grupo sobre el mismo módulo de Odoo. Léelo antes de tu primer commit.

**Principio básico:** cada modelo es una unidad completa. Modelo, vistas, acción, menú y permisos van **juntos** en la misma rama, el mismo issue y el mismo pull request. Una vista no se puede probar sin su modelo, así que no los separamos. La única excepción es cuando otros modelos dependen del tuyo (ver sección 2.6).

## 1. Convenciones de nombres

- **Modelo técnico**: `uprofe.<entidad_en_minusculas>`, ej. `uprofe.profesor`, `uprofe.detalle_matricula`. Nunca camelCase. En español pero sin acentos ni caracteres especiales.
- **Archivo Python**: un archivo por modelo en `models/<entidad>.py`, registrado en `models/__init__.py` con `from . import <entidad>`.
- **Campos relacionales**: sufijo `_id` para M2O (`grupo_id`), sufijo `_ids` para O2M/M2M (`asistencia_ids`, `tema_ids`).
- **IDs de vistas**: `view_<modelo>_<tipo>` (`view_profesor_tree`, `view_profesor_form`, `view_profesor_calendar`).
- **Archivo de vistas**: `views/<modelo>_views.xml`, uno por modelo — no mezclar varios modelos en el mismo archivo.
- **Commits**: mensaje con el modelo entre corchetes, ej. `[sesion] añade validación de horas y vista calendar`.
- **Ramas**: `feature/<persona>-<modelo>`, ej. `feature/aurelio-sesion`. Una rama corta por modelo (incluye modelo **y** vistas), no una rama única por persona. Por defecto no se separan ramas para modelo y vista; solo se hace en el caso de dependencias descrito en la sección 2.6.

## 2. Flujo de trabajo

### 2.1 Antes de empezar un modelo nuevo

Comprueba que existe el issue del modelo y que está asignado a ti. Después:

```bash
git checkout main
git pull origin main
git checkout -b feature/<persona>-<modelo>
```

Esto asegura que partes de la última versión de `main` y trabajas en un espacio aislado que no afecta al código de nadie más. También puedes crear la rama desde el propio issue (barra lateral → **Development → Create a branch**), respetando el nombre anterior.

Si tu modelo depende de otro (por ejemplo, un `Many2one` a un modelo de otra persona), mira antes si ese modelo ya está en `main`. Si no lo está, indícalo en el issue con `Depende de #N` y coordínate con quien lo desarrolla. Sigue lo descrito en la sección 2.6.

### 2.2 Mientras trabajas

Commits pequeños y descriptivos (modelo, vistas, etc):

```bash
git add models/<modelo>.py
git commit -m "[<modelo>] añade modelo con campos básicos y relación a X"
```

Trabaja en ramas cortas: abre el PR en cuanto el modelo esté completo, sin esperar semanas.

**Archivos compartidos.** Estos archivos los toca todo el mundo y son la fuente principal de conflictos:

- `__manifest__.py`
- `models/__init__.py`
- `security/ir.model.access.csv`

Para reducir conflictos: añade solo **tus** líneas, no reformatees ni reordenes las de los demás, y respeta un archivo por modelo y un archivo de vistas por modelo.

### 2.3 Antes de abrir el pull request

1. Actualiza tu rama con los últimos cambios de `main`:

   ```bash
   git fetch origin
   git rebase origin/main
   ```

   Resuelve los conflictos en local, no en GitHub.

2. Instala o actualiza el módulo en Odoo (`-u uprofe`) y comprueba que arranca sin errores y que tus vistas se abren correctamente.

### 2.4 Al terminar: pull request

El pull request **no se crea con git**, se crea desde la interfaz de GitHub, después de subir la rama:

```bash
git push origin feature/<persona>-<modelo>
```

(Si hiciste rebase después de un push anterior, usa `git push --force-with-lease`.)

1. En GitHub, pulsa **Compare & pull request** (o **Pull requests → New pull request**).
2. Confirma `base: main` ← `compare: feature/<persona>-<modelo>`.
3. Título corto: `[<modelo>] modelo, vistas y validaciones`.
4. Descripción (incluye `Closes #N` para que el issue se cierre solo al fusionar; si es un PR solo de modelo por una dependencia, usa `Refs #N`, ver 2.6):

   ```
   Closes #<número del issue>

   ## Qué incluye
   - Modelo uprofe.<modelo> ...
   - Vistas tree, form, [calendar/graph/...] ...
   - Validaciones
   - Etc.

   ## Comprobado
   - [ ] El módulo se instala/actualiza sin errores
   - [ ] Las vistas se abren y se pueden crear/editar registros
   - [ ] Permisos añadidos en ir.model.access.csv
   ```
5. Pulsa **Create pull request**.
6. Otra persona del grupo revisa en **Files changed** y pulsa **Review changes → Approve**.
7. Con la aprobación, pulsa **Merge pull request**. Esto fusiona a `main`.
8. Borra la rama una vez fusionada (GitHub ofrece el botón **Delete branch**). No pasa nada por borrarla: el trabajo ya está en `main`, y el pull request cerrado conserva todos los commits, los cambios y la revisión, de modo que se sigue viendo quién hizo qué. Si hiciera falta, el propio PR tiene un botón **Restore branch**.

### 2.5 Issues y Project

Los issues y el Project son dos objetos distintos que hay que conectar explícitamente — no van unidos por defecto.

- **Issues** (dentro del repo): **un issue por modelo** (`Modelo: uprofe.<modelo>`), asignado a la persona responsable. Cubre modelo **y** vistas; no se crean issues separados para la vista ni sub-issues. Son la capa de gestión (qué falta, quién lo hace); las ramas y PRs son la capa de trabajo (el código en sí).

  Cada issue lleva este checklist para llevar el detalle sin multiplicar elementos:

  ```
  - [ ] Modelo
  - [ ] Vistas
  ```

  Si el modelo depende de otro, añade en la descripción `Depende de #N`.

- **Etiquetas** recomendadas: `bloqueado` (esperando a otro modelo), `dependencia` (otros modelos dependen de este, fusionar cuanto antes) y `bug`.

- **Project** (tablero Kanban Pendiente / Listo para empezar / En progreso / En revisión / Hecho): es la vista de conjunto del trabajo del grupo. Un issue no aparece ahí solo — hay que añadirlo con una de estas dos opciones:

  1. Desde el Project: **+ Add item** → buscar el issue por número o título.

  2. Desde el issue: barra lateral derecha → sección **Projects** → seleccionar el tablero.

- Una vez el issue está en el Project, **el estado de la tarjeta se puede actualizar manualmente** según avance el trabajo (los workflows del Project también pueden moverlo solos al abrir o fusionar un PR vinculado):

  - **Pendiente** → modelo todavía sin empezar.
  - **Listo para empezar** → no depende de ningún modelo pendiente, ya se puede empezar.
  - **En progreso** → alguien está trabajando en el issue.
  - **En revisión** → el trabajo está terminado y hay un PR abierto para revisarlo.
  - **Hecho** → el trabajo ha sido revisado y fusionado.

### 2.6 Cuando otros modelos dependen del tuyo

**Regla por defecto:** una rama y un PR por modelo, con modelo y vistas juntos. Solo cuando otra persona necesita tu modelo (por ejemplo, tiene un `Many2one` hacia él) y tus vistas van a tardar, se divide el trabajo en **dos ramas y dos PRs**. Esta división se decide en el issue: la persona que depende lo pide con un comentario, y se marca el issue con la etiqueta `dependencia`.

**Orden de fusión:** siempre primero el modelo del que se depende, luego el que depende.

#### Lo que hace quien tiene el modelo del que dependen

1. **Rama del modelo**: `feature/<persona>-<modelo>`. Contiene solo el modelo, su `import` y su línea en `ir.model.access.csv`, de forma que el módulo se instale sin errores. Las vistas quedan para después.
2. **PR del modelo**: descripción con `Refs #N`, donde `N` es el número del issue del modelo, el que aparece junto al título en GitHub (por ejemplo, `Refs #12`). No uses `Closes #N`, porque el issue aún no está completo. Avisa en el issue de que está listo y pide revisión con prioridad.
3. **Rama de las vistas**: cuando el PR del modelo esté fusionado, crea una rama nueva desde `main` actualizado:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/<persona>-<modelo>-vistas
   ```

4. **PR de las vistas**: descripción con `Closes #N`, que ahora sí cierra el issue.

#### Lo que hace quien depende del modelo

**Todo el grupo sigue la misma opción por defecto: esperar al merge.** Mientras tanto, trabaja en lo que no dependa de ese modelo y, cuando el PR del modelo esté fusionado, actualiza su rama:

```bash
git fetch origin
git rebase origin/main
```

La alternativa (crear tu rama desde la rama de otra persona con `git checkout -b feature/<persona>-<modelo> origin/feature/<otra-persona>-<modelo>`) es una **excepción** y solo se usa si de verdad no puedes avanzar sin ver ese modelo. Antes hay que acordarla con la otra persona en el issue, porque tiene costes: tienes que traer sus cambios cada vez que modifique algo, tu PR no se puede fusionar antes que el suyo, y al fusionarse el suyo tendrás que hacer `git rebase origin/main` para limpiar tu historial.

Se usa una única opción por defecto para todo el grupo porque así todos saben qué esperar y se evitan historiales mezclados y conflictos difíciles de resolver.

#### Etiquetas

- Issue de quien depende: `bloqueado` y `Depende de #N` en la descripción, hasta que el modelo esté en `main`.
- Issue de quien tiene el modelo: `dependencia`, para que se revise antes.
- Al fusionarse el PR del modelo, se quita `bloqueado` del otro issue.

## 3. Reglas de main

- `main` está protegida: nadie hace push directo, todo entra por pull request.
- Se requiere al menos 1 aprobación de otra persona del grupo antes de poder fusionar.
- Un PR debe poder instalarse sobre `main` sin romper el módulo. Si no arranca, no se fusiona.
