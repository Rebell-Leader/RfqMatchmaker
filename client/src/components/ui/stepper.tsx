import { cn } from "@/lib/utils";

export interface StepperProps {
  steps: { id: number; label: string }[];
  currentStep: number;
  className?: string;
}

export function Stepper({ steps, currentStep, className }: StepperProps) {
  return (
    <div className={cn("bg-white border-b", className)}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center overflow-x-auto">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center shrink-0">
              {/* Step circle */}
              <div className="flex items-center">
                <div
                  className={cn(
                    "flex items-center justify-center w-8 h-8 rounded-full text-sm",
                    step.id < currentStep
                      ? "bg-secondary text-white" // completed
                      : step.id === currentStep
                      ? "bg-primary text-white" // active
                      : "bg-gray-200 text-gray-600" // pending
                  )}
                >
                  {step.id}
                </div>
                <div className="text-sm ml-2 font-medium">{step.label}</div>
              </div>

              {/* Connector line */}
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    "h-0.5 w-16 mx-2",
                    step.id < currentStep
                      ? "bg-secondary" // completed
                      : step.id === currentStep
                      ? "bg-primary" // active
                      : "bg-gray-200" // pending
                  )}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
