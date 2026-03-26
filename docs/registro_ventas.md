# Registro de Ventas — Cuervo Negro Barber & Tattoo

> Sistema de gestión v1.0 | Módulo: Operaciones > Nueva Venta

---

## ¿Qué es una Venta?

Una **Venta** registra el cobro de uno o más servicios y/o productos realizados en el local. Queda asociada a:

- Un **barbero** que ejecutó el trabajo (obligatorio)
- Un **cliente** del sistema (opcional, puede ser venta anónima)
- Una **cita** previa del calendario (opcional, para cerrar el ciclo)
- Uno o más **ítems** (servicios o productos del inventario)
- Un **método de pago** (Efectivo, QR/Transferencia, Tarjeta)

---

## Flujo general del registro

```
1. Seleccionar barbero
       ↓
2. Buscar cliente (opcional)
       ↓
3. Vincular cita del día (opcional)
       ↓
4. Agregar ítems (servicios y/o productos)
       ↓
5. Aplicar descuento (opcional)
       ↓
6. Seleccionar método de pago
       ↓
7. Confirmar y registrar
       ↓
8. Ver detalle / recibo de la venta
```

---

## Pantalla Nueva Venta (`/ventas/nueva/`)

### Sección 1 — Barbero

Selecciona el barbero que atendió al cliente haciendo clic en su tarjeta. Si solo hay un barbero registrado se selecciona automáticamente.

Al seleccionar barbero, el sistema carga automáticamente las **citas pendientes o confirmadas del día** de ese barbero.

### Sección 2 — Cliente *(opcional)*

- Escribe el nombre o teléfono del cliente en el buscador.
- El sistema filtra en tiempo real desde la base de datos.
- Si no aparece en la lista, la venta se registra como **venta anónima** (sin cliente vinculado).
- El cliente puede desvincularse en cualquier momento con el botón "✖ Quitar cliente".

### Sección 3 — Vincular cita *(opcional)*

Aparece cuando el barbero tiene citas activas ese día. Al hacer clic en una cita:
- Se autoselecciona el cliente de esa cita.
- Al registrar la venta, la cita queda marcada automáticamente como **Atendida**.
- El precio cobrado se actualiza en la cita.

### Sección 4 — Ítems de la venta

| Tipo       | Descripción                                                 |
|------------|-------------------------------------------------------------|
| Servicio   | Servicios registrados en el catálogo (corte, barba, etc.)   |
| Producto   | Productos del inventario (pomadas, aceites, etc.)           |

**Agregar un ítem:**
1. Clic en **+ SERVICIO** o **+ PRODUCTO**
2. Seleccionar el ítem del desplegable (el precio se rellena automáticamente)
3. Ajustar la cantidad si es necesario
4. Modificar el precio si aplica un precio especial

**Para productos:** se muestra el stock disponible. Si el stock es ≤ 3 se resalta en rojo como advertencia. Al guardar la venta, el stock se descuenta automáticamente y queda registrado en el historial de movimientos del inventario.

Se pueden agregar múltiples ítems mezclando servicios y productos.

### Sección 5 — Totales

- **Subtotal:** suma de todos los ítems (precio × cantidad)
- **Descuento:** monto fijo a descontar en Bolivianos
- **Total:** subtotal − descuento

### Sección 6 — Método de pago

| Método       | Icono | Descripción                      |
|--------------|-------|----------------------------------|
| Efectivo     | 💵    | Pago en efectivo con cálculo de vuelto |
| QR           | 📱    | Transferencia bancaria o código QR    |
| Tarjeta      | 💳    | Tarjeta de débito o crédito          |

**Para pagos en efectivo:** el sistema calcula el vuelto en tiempo real. Botones rápidos de Bs.20 / 50 / 100 / 200 agilizan el registro.

---

## Casos de uso comunes

### Caso 1 — Corte simple con pago en efectivo

> El cliente entra sin cita previa, paga en efectivo.

1. Seleccionar barbero → **Ej. Carlos Mendoza**
2. Cliente: dejar vacío (venta anónima) o buscar si ya está registrado
3. No vincular cita
4. **+ SERVICIO** → "Corte Clásico" → precio Bs.50, cantidad 1
5. Descuento: 0
6. Método: **Efectivo** → cliente entrega Bs.100 → vuelto: Bs.50
7. **REGISTRAR VENTA** ✔

---

### Caso 2 — Combo corte + barba con cita previa

> El cliente tenía cita confirmada en la agenda, paga con QR.

1. Seleccionar barbero → aparecen las citas del día
2. Hacer clic en la cita del cliente → se autoselecciona el cliente
3. **+ SERVICIO** → "Combo Corte + Barba" → Bs.90
4. Método: **QR**
5. **REGISTRAR VENTA** ✔ → la cita queda automáticamente como "Atendida"

---

### Caso 3 — Servicio + venta de producto

> El cliente se corta el pelo y también compra una pomada.

1. Seleccionar barbero
2. Buscar cliente → ej. "Juan Quispe"
3. **+ SERVICIO** → "Corte Degradado" → Bs.60
4. **+ PRODUCTO** → "Pomada Fijadora" → Bs.35, stock visible
5. Total: Bs.95
6. Método: **Efectivo**
7. **REGISTRAR VENTA** ✔ → stock de pomada se descuenta en -1 automáticamente

---

### Caso 4 — Descuento por cliente frecuente

> Cliente habitual con 10% de descuento.

1. Seleccionar barbero y cliente
2. Agregar ítems → subtotal: Bs.110
3. Descuento: **Bs.11** (10%)
4. Total final: **Bs.99**
5. Registrar ✔

---

### Caso 5 — Precio especial en momento de cobro

> El precio pactado difiere del precio del catálogo.

1. Agregar ítem normalmente → precio se rellena del catálogo
2. **Editar el campo "Precio"** directamente en la fila del ítem
3. El total se recalcula en tiempo real
4. Registrar ✔

> ℹ️ El precio modificado queda registrado en el ítem de venta. El precio del catálogo no se modifica.

---

### Caso 6 — Múltiples servicios (tatuaje + sesión)

> Cliente paga sesión de tatuaje y toque-up del mes anterior.

1. Seleccionar barbero/tatuador
2. Buscar cliente
3. **+ SERVICIO** → "Sesión Tattoo" → Bs.300
4. **+ SERVICIO** → "Toque-up" → Bs.80 (precio especial: Bs.50)
   - Editar precio a Bs.50 manualmente
5. Total: Bs.350
6. Método: **Tarjeta**
7. Registrar ✔

---

## Efectos al registrar una venta

| Elemento                | Qué ocurre                                          |
|-------------------------|-----------------------------------------------------|
| Venta                   | Se crea registro con items, totales y método de pago |
| Inventario              | Stock de productos vendidos se descuenta            |
| Movimiento de stock     | Se registra salida en el historial del producto      |
| Cita vinculada          | Estado cambia a **Atendida**, precio cobrado guardado |
| Corte de caja           | La venta queda disponible para el cierre del día    |

---

## Corte de Caja (`/ventas/corte-caja/`)

Al finalizar el día, el módulo de **Corte de Caja** muestra:

- Total de ventas del día por método de pago (Efectivo / QR / Tarjeta)
- Lista de todas las transacciones del día
- Botón para **cerrar la caja** (registra el corte con sello de fecha y usuario)

Solo se puede realizar **un corte por día**. Si ya existe uno, el sistema lo indica.

---

## Errores comunes y soluciones

| Error                              | Causa                                       | Solución                              |
|------------------------------------|---------------------------------------------|---------------------------------------|
| "Selecciona un barbero"            | No se eligió barbero antes de registrar     | Hacer clic en una tarjeta de barbero  |
| "Agrega al menos un ítem"          | La venta está vacía                         | Agregar servicio o producto           |
| "Selecciona el ítem en todas las filas" | Fila agregada pero sin selección       | Seleccionar ítem o eliminar la fila   |
| Stock insuficiente (error backend) | Producto sin stock disponible               | Verificar stock en Inventario > Alertas |
| Conflicto de cita                  | La cita ya tiene una venta asociada         | Usar "Vincular cita" solo una vez     |

---

## Permisos

| Rol             | Puede registrar ventas | Puede ver lista | Puede hacer corte de caja |
|-----------------|------------------------|-----------------|---------------------------|
| Admin           | ✔                      | ✔               | ✔                         |
| Recepcionista   | ✔                      | ✔               | ✔                         |
| Barbero         | ✔ (solo propias)       | ✔ (solo propias)| ✗                         |

---

*Documento generado para el sistema Cuervo Negro Barber & Tattoo — v1.0*
