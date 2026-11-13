import { fireEvent, render, screen } from "@testing-library/react";
import { BeforeAfterSlider } from "@/components/BeforeAfterSlider";

test("el comparador se controla con el deslizador accesible", () => {
  render(<BeforeAfterSlider before="/a.png" after="/b.png" />);
  const slider = screen.getByRole("slider", { name: "Comparar antes y después" });
  fireEvent.change(slider, { target: { value: "30" } });
  expect(screen.getByAltText("Imagen original")).toHaveStyle({ clipPath: "inset(0 70% 0 0)" });
  expect(screen.getByAltText("Resultado editado con IA")).toBeInTheDocument();
});
