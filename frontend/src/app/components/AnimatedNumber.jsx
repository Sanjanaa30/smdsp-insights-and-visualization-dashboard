import dynamic from "next/dynamic";
const AnimatedNumbers = dynamic(() => import("react-animated-numbers"), {
  ssr: false,
});

export default function AnimatedNumber({ value }) {
  return (
    <AnimatedNumbers
      useThousandsSeparator
      transitions={(index) => ({
        type: "spring",
        duration: index + 0.3,
      })}
      animateToNumber={value}
      className="text-2xl font-semibold text-gray-900"
    />
  );
}
