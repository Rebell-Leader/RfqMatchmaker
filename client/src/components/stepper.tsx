import { FC } from "react";
import { Link } from "wouter";
import { cn } from "@/lib/utils";

interface StepperProps {
  currentStep: number;
  rfqId?: number;
}

interface Step {
  number: number;
  title: string;
  path: string;
}

const Stepper: FC<StepperProps> = ({ currentStep, rfqId }) => {
  const steps: Step[] = [
    { number: 1, title: "Upload RFQ", path: "/" },
    { number: 2, title: "Review Requirements", path: rfqId ? `/review/${rfqId}` : "/review" },
    { number: 3, title: "Match Suppliers", path: rfqId ? `/match/${rfqId}` : "/match" },
    { number: 4, title: "Score Results", path: rfqId ? `/score/${rfqId}` : "/score" },
    { number: 5, title: "Send Proposals", path: rfqId ? `/proposals/${rfqId}` : "/proposals" },
  ];

  return (
    <div className="bg-white border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-wrap items-center gap-2 md:gap-0">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center">
              <div className="flex items-center">
                <div 
                  className={cn(
                    "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
                    step.number < currentStep && "bg-green-600 text-white", // completed
                    step.number === currentStep && "bg-primary text-white", // active
                    step.number > currentStep && "bg-gray-200 text-gray-500" // pending
                  )}
                >
                  {step.number < currentStep ? (
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      className="h-5 w-5" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path 
                        fillRule="evenodd" 
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                        clipRule="evenodd" 
                      />
                    </svg>
                  ) : (
                    step.number
                  )}
                </div>
                
                <div className="ml-2 text-sm font-medium hidden md:block">
                  {step.number < currentStep ? (
                    <Link href={step.path} className="text-gray-700 hover:text-primary">
                      {step.title}
                    </Link>
                  ) : (
                    <span className={step.number === currentStep ? "text-primary" : "text-gray-500"}>
                      {step.title}
                    </span>
                  )}
                </div>
              </div>
              
              {index < steps.length - 1 && (
                <div 
                  className={cn(
                    "w-16 h-0.5 mx-2 hidden md:block",
                    index < currentStep - 1 && "bg-green-600",
                    index === currentStep - 1 && "bg-primary",
                    index >= currentStep && "bg-gray-200"
                  )}
                ></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Stepper;
