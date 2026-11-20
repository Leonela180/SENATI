// MÓDULO CHATBOT · Guía local: lo que responde el asistente SIN Gemini (sin internet, sin clave o sin consentimiento).
//
// ¿Quieres agregar o cambiar una pregunta/respuesta? Edita RECIPES:
//   name  → título que se muestra (y botón en «Objetivos rápidos»)
//   words → palabras que la activan (minúsculas y SIN tildes: «antigu» encuentra «antigua» y «antiguo»)
//   tool  → herramienta a la que lleva el botón (debe existir en TOOL_LINKS)
//   steps → pasos que se muestran
//   limit → aviso honesto de lo que la herramienta no hace
// Se usa la PRIMERA receta cuyas palabras coincidan, así que el orden importa.
//
// Las instrucciones para Gemini (respuestas con IA) están en backend/app/services/asistente_instrucciones.py.

export type Recipe = { name: string; words: RegExp; tool: string; steps: string[]; limit: string };

export const BIENVENIDA = "¡Hola! Soy el asistente de LUMIA. Dime qué quieres mejorar en tu foto y te digo cómo hacerlo.";
export const SIN_COINCIDENCIA = "No encontré un recorrido para eso. Prueba con «restaurar foto antigua», «cambiar fondo», «quitar lunar» o «reducir ruido», o elige un objetivo de la lista.";

// Botones de ejemplo que aparecen al abrir el chat.
export const SUGERENCIAS = ["Mi foto antigua tiene rayas y está opaca", "Quiero un fondo blanco para mi CV", "Tengo un lunar en la mejilla", "Mi retrato de IA se ve muy plástico"];

export const RECIPES: Recipe[] = [
  { name: "Solicitar o revisar un permiso", words: /permiso|lider|jefe|equipo|invit|grupo/, tool: "equipo", steps: ["Abre Equipo. Quien crea el espacio es su líder dentro de LUMIA.", "Como integrante, indica Desde, Hasta y Motivo en Permisos del equipo.", "El líder revisa y aprueba o rechaza; tú puedes consultar la respuesta o cancelar mientras esté pendiente."], limit: "No verifica cargos legales ni modifica automáticamente tus horas. Solo tú y el líder ven el motivo." },
  { name: "Personalizar mi espacio", words: /avatar|tema|oscuro|claro|personaliz|color de la pagina/, tool: "perfil", steps: ["Abre Perfil y la sección Tu estilo.", "Elige avatar, acento y apariencia; los cambios se aplican al instante.", "Puedes restablecer las preferencias en cualquier momento."], limit: "Las preferencias se guardan en este navegador, no se sincronizan entre dispositivos." },
  { name: "Convertir una ilustración", words: /pixar|disney|ilustr|personaje|convertir|dibujo/, tool: "realista", steps: ["Abre Ilustración a realista en el laboratorio.", "Revisa si el modo está habilitado: necesita una validación de calidad y un motor real compatible.", "Si está disponible, elige un personaje adulto y confirma tu permiso de uso."], limit: "Es experimental y puede cambiar los rasgos. No se garantiza una conversión fiel ni se ofrece mientras esté deshabilitado." },
  { name: "Quitar el aspecto de plástico", words: /plastic|artificial|piel lisa|muy lis|muneca|poros|textura/, tool: "textura_piel", steps: ["Abre el retrato en Textura de piel realista. Empieza con intensidad al 60–70 %.", "Compara con el deslizador: los poros deben verse de cerca, no desde lejos.", "Si quieres más naturalidad, después usa Humanizar o activa las pecas suaves."], limit: "Es un filtro digital: agrega textura a la piel detectada; no cambia la forma del rostro ni corrige la iluminación." },
  { name: "Recuperar una foto antigua", words: /antigu|vieja|restaur|rayad|deterior|descolor|recuerdo/, tool: "restaurar", steps: ["Abre la foto en Restaurar foto. Empieza con recuperación de tonos al 40–60 %.", "Marca solo las rayas o manchas pequeñas. Ajusta el pincel para no tocar ojos ni contornos.", "Compara el resultado y guarda una copia antes de seguir editando."], limit: "La restauración corrige tonos y daños pequeños; no recupera información inexistente ni colorea automáticamente." },
  { name: "Preparar un retrato profesional", words: /fondo|profesional|cv|curricul|recort|transparent/, tool: "cambiar_fondo", steps: ["Selecciona Cambiar fondo y elige un color neutro o transparencia.", "Revisa los bordes del cabello y los hombros antes de descargar.", "Guarda el resultado y aplica Ajustes si necesitas corregir la luz."], limit: "Los cabellos finos y fondos complejos pueden necesitar otra fotografía." },
  { name: "Reparar una mancha localizada", words: /lunar|mancha|grano|borrar|quitar/, tool: "quitar_lunar", steps: ["Elige Quitar lunar y marca el centro de la mancha.", "Usa un pincel apenas mayor que la zona; evita cubrir rasgos completos.", "Aplica y compara la textura con la piel de alrededor."], limit: "El relleno utiliza píxeles vecinos. No es apropiado para eliminar objetos grandes." },
  { name: "Conseguir efecto retrato", words: /desenfo|gaus|bokeh|retrato/, tool: "desenfoque", steps: ["Selecciona Desenfoque y la zona Fondo.", "Empieza con un radio de 4–8 y conserva el rostro enfocado.", "Revisa la separación entre persona y fondo en la comparación."], limit: "Desenfocar una foto no permite recuperar después sus detalles perdidos." },
  { name: "Ampliar una imagen", words: /ruido|pixel|nitid|calidad|resoluc|borros|ampli|grande/, tool: "mejorar_calidad", steps: ["Abre Mejorar calidad y elige ×2 o ×4 (máximo 4096 px por lado).", "Deja la nitidez suave (0,3–0,5); activa Reducir ruido solo si la imagen tiene grano visible.", "Compara de cerca: los bordes no deben verse dibujados."], limit: "Es una ampliación digital: no es 4K real ni recupera detalles que no estaban en el original." },
  { name: "Corregir luz y color", words: /luz|oscura|brillo|color|contraste|satur/, tool: "ajustes", steps: ["Abre Ajustes y corrige primero el brillo.", "Modifica contraste y saturación en pasos pequeños.", "Comprueba que piel, blancos y sombras mantengan un aspecto natural."], limit: "Las zonas completamente blancas o negras pueden carecer de detalle recuperable." },
];

// A dónde lleva el botón «Abrir herramienta» de cada identificador.
export const TOOL_LINKS: Record<string, { label: string; to: string }> = {
  equipo: { label: "Equipo y permisos", to: "/app/equipo" },
  horas: { label: "Horario y horas", to: "/app/horas" },
  perfil: { label: "Personalizar mi espacio", to: "/app/perfil" },
  realista: { label: "Laboratorio realista", to: "/app/realista" },
  humanizar: { label: "Humanizar", to: "/app/humanizar" },
  galeria: { label: "Galería", to: "/app/galeria" },
  restaurar: { label: "Restaurar foto", to: "/app/estudio?tool=restaurar" },
  quitar_lunar: { label: "Quitar lunar", to: "/app/estudio?tool=quitar_lunar" },
  cambiar_fondo: { label: "Cambiar fondo", to: "/app/estudio?tool=cambiar_fondo" },
  desenfoque: { label: "Desenfoque", to: "/app/estudio?tool=desenfoque" },
  mejorar_calidad: { label: "Mejorar calidad", to: "/app/estudio?tool=mejorar_calidad" },
  ajustes: { label: "Ajustes", to: "/app/estudio?tool=ajustes" },
  textura_piel: { label: "Textura de piel", to: "/app/estudio?tool=textura_piel" },
};

// Busca la receta que coincide con lo que escribió la persona.
export function buscarReceta(text: string): Recipe | undefined {
  const normalized = text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  return RECIPES.find(r => r.words.test(normalized));
}
