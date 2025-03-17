import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { FaBolt, FaSearch, FaChartBar, FaFileAlt, FaLaptop, FaMicrochip } from "react-icons/fa";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Cpu, Globe, Zap, Shield, BarChart4 } from "lucide-react";
import { useDemoMode } from "@/context/demo-context";

export default function Landing() {
  const [, navigate] = useLocation();
  const { isDemoMode, toggleDemoMode } = useDemoMode();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      {/* Hero Section */}
      <section className="relative py-20 px-6 md:px-10 max-w-7xl mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-cyan-500/10 to-transparent rounded-3xl" style={{ zIndex: -1 }}></div>
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-4">
              <Cpu className="w-4 h-4 mr-2" />
              <span>AI Hardware Procurement Simplified</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold mb-6 bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Find the Perfect AI Accelerators for Your Machine Learning Workloads
            </h1>
            <p className="text-xl mb-8 text-slate-700">
              Our specialized platform helps you navigate complex AI hardware procurement, 
              from compliance verification to performance benchmarking and global supplier matching.
            </p>
            <div className="flex flex-wrap gap-4">
              <Button 
                size="lg" 
                className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
                onClick={() => navigate("/upload")}
              >
                Start Procurement
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                className="text-lg px-8 py-6 border-blue-300 text-blue-700 hover:bg-blue-50"
                onClick={() => navigate("/ai-hardware")}
              >
                Explore AI Platform
              </Button>
            </div>
          </div>
          <div className="relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-lg opacity-75 blur"></div>
            <div className="relative bg-slate-900 p-8 rounded-lg shadow-lg">
              <div className="bg-slate-800 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-green-400 text-sm">NVIDIA H100</span>
                  </div>
                  <span className="text-cyan-400 text-xs">989 TFLOPs</span>
                </div>
                
                <div className="space-y-2.5">
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Memory</span>
                      <span>80GB HBM3</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-700 rounded-full">
                      <div className="h-1.5 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full" style={{ width: '90%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Bandwidth</span>
                      <span>3.3 TB/s</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-700 rounded-full">
                      <div className="h-1.5 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full" style={{ width: '95%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                      <span>Framework Support</span>
                      <span>Complete</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-700 rounded-full">
                      <div className="h-1.5 bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <div className="flex items-center bg-slate-900/50 p-1.5 rounded text-xs text-slate-300">
                    <div className="w-2 h-2 rounded-full bg-green-500 mr-1.5"></div>
                    <span>Export Compliant</span>
                  </div>
                  <div className="flex items-center bg-slate-900/50 p-1.5 rounded text-xs text-slate-300">
                    <div className="w-2 h-2 rounded-full bg-amber-500 mr-1.5"></div>
                    <span>35 Day Delivery</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-4 gap-2">
                <div className="h-1.5 bg-blue-600 rounded-full"></div>
                <div className="h-1.5 bg-blue-500 rounded-full"></div>
                <div className="h-1.5 bg-cyan-500 rounded-full"></div>
                <div className="h-1.5 bg-cyan-400 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem/Solution Section */}
      <section className="py-16 px-6 max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold mb-4 text-red-600">The AI Hardware Challenge</h2>
              <p className="text-slate-700">
                Procuring the right AI accelerators is increasingly complex due to geopolitical restrictions,
                diverse performance metrics, and specialized hardware requirements. Many organizations struggle with 
                comparing options across manufacturers while ensuring compliance and optimal performance.
              </p>
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-4 text-blue-600">Our Specialized Solution</h2>
              <p className="text-slate-700">
                Our AI hardware platform analyzes technical requirements, verifies export compliance, 
                benchmarks performance for your specific workloads, and matches you with available suppliers. 
                We streamline procurement while ensuring regulatory compliance and maximizing ML/AI performance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-6 bg-gradient-to-b from-slate-100 to-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">AI Hardware Procurement Features</h2>
          <p className="text-lg text-center text-slate-600 mb-12 max-w-3xl mx-auto">
            Our platform provides specialized features designed for the unique challenges of AI hardware procurement, 
            ensuring you find the optimal balance of performance, compliance, and value.
          </p>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-blue-200 hover:border-blue-500 hover:shadow-blue-100 transition-all">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center mb-4 text-white">
                <Globe className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Global Compliance Checks</h3>
              <p className="text-slate-600">
                Automatically verify export restrictions and compliance requirements
                for AI hardware across different regions and jurisdictions.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-blue-200 hover:border-blue-500 hover:shadow-blue-100 transition-all">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center mb-4 text-white">
                <BarChart4 className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Performance Benchmarks</h3>
              <p className="text-slate-600">
                Compare accelerator performance across different models and workloads, 
                including FP16/FP32 performance, memory bandwidth, and ML benchmarks.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-blue-200 hover:border-blue-500 hover:shadow-blue-100 transition-all">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center mb-4 text-white">
                <Shield className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Framework Compatibility</h3>
              <p className="text-slate-600">
                Verify hardware compatibility with popular ML frameworks like PyTorch, 
                TensorFlow, and JAX to ensure seamless integration with your stack.
              </p>
            </div>
            
            {/* Feature 4 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-blue-200 hover:border-blue-500 hover:shadow-blue-100 transition-all">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center mb-4 text-white">
                <Zap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Intelligent Matching</h3>
              <p className="text-slate-600">
                Match your specific AI workload requirements with the optimal hardware solutions
                based on performance benchmarks, cooling requirements, and power constraints.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* AI Hardware Platform Section */}
      <section className="py-16 px-6 bg-gradient-to-b from-white to-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="bg-slate-900 p-8 rounded-lg shadow-xl text-white overflow-hidden relative">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-tr from-green-500/20 to-cyan-500/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/3"></div>
            
            <div className="grid md:grid-cols-2 gap-8 items-center relative z-10">
              <div>
                <div className="flex items-center mb-4">
                  <Cpu className="text-cyan-400 mr-2 h-6 w-6" />
                  <span className="text-cyan-400 uppercase tracking-wider text-sm font-semibold">New Platform</span>
                </div>
                
                <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  Specialized AI Hardware Procurement Platform
                </h2>
                
                <p className="text-slate-300 mb-6">
                  Finding the right AI accelerators and GPUs for your machine learning workloads is complex.
                  Our specialized platform handles compliance checks, performance benchmarking, and global sourcing
                  to match you with the perfect hardware solutions.
                </p>
                
                <div className="flex flex-wrap gap-4 mb-6">
                  <div className="bg-slate-800 px-3 py-1 rounded-full text-xs text-slate-300 flex items-center">
                    <FaMicrochip className="mr-1 text-cyan-500" />
                    GPU Matching
                  </div>
                  <div className="bg-slate-800 px-3 py-1 rounded-full text-xs text-slate-300 flex items-center">
                    <FaMicrochip className="mr-1 text-cyan-500" />
                    Export Compliance
                  </div>
                  <div className="bg-slate-800 px-3 py-1 rounded-full text-xs text-slate-300 flex items-center">
                    <FaMicrochip className="mr-1 text-cyan-500" />
                    Performance Benchmarks
                  </div>
                </div>
                
                <Button 
                  variant="outline" 
                  className="text-white border-cyan-500 hover:bg-cyan-500/20"
                  onClick={() => navigate("/ai-hardware")}
                >
                  Explore AI Hardware Platform
                </Button>
              </div>
              
              <div>
                <div className="relative bg-slate-800 p-4 rounded-lg shadow-lg">
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-lg opacity-50"></div>
                  <div className="relative">
                    <div className="bg-slate-700 rounded p-3 mb-4">
                      <div className="flex justify-between text-xs text-slate-400 mb-2">
                        <span>GPU Performance Comparison</span>
                        <span>TFLOPs</span>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-cyan-400">NVIDIA A100</span>
                            <span className="text-slate-300">312 TFLOPs</span>
                          </div>
                          <div className="w-full bg-slate-600 rounded-full h-2">
                            <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-cyan-400">AMD MI250X</span>
                            <span className="text-slate-300">383 TFLOPs</span>
                          </div>
                          <div className="w-full bg-slate-600 rounded-full h-2">
                            <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full" style={{ width: '95%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-cyan-400">Intel Gaudi2</span>
                            <span className="text-slate-300">197 TFLOPs</span>
                          </div>
                          <div className="w-full bg-slate-600 rounded-full h-2">
                            <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-xs text-slate-400 mb-1">Regional Availability</div>
                    <div className="bg-slate-700 p-3 rounded grid grid-cols-2 gap-2">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                        <span className="text-xs text-slate-300">North America</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                        <span className="text-xs text-slate-300">Europe</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></div>
                        <span className="text-xs text-slate-300">Asia Pacific</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                        <span className="text-xs text-slate-300">Restricted Regions</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-6 max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <h2 className="text-3xl lg:text-4xl font-bold mb-5 bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
            AI Hardware Procurement Process
          </h2>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto">
            Our specialized platform streamlines complex AI hardware procurement, ensuring you get 
            the optimal hardware for your machine learning and AI workloads.
          </p>
        </div>
        
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-8 lg:p-10 rounded-xl shadow-xl text-white">
          <h3 className="text-xl font-semibold mb-8 text-center text-cyan-400">
            Example: AI Accelerator Procurement for ML Cloud Training Platform
          </h3>
          
          <div className="grid md:grid-cols-5 gap-6 mt-10 relative">
            {/* Connecting line */}
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-blue-500 to-cyan-400 transform -translate-y-1/2 hidden md:block" style={{ zIndex: 0 }}></div>
            
            <div className="flex flex-col items-center text-center relative z-10">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-full flex items-center justify-center mb-5 text-xl font-bold shadow-lg">1</div>
              <h4 className="font-semibold text-blue-300 mb-2">Submit Requirements</h4>
              <p className="text-slate-300 text-sm">Upload RFQ with detailed AI hardware specs, frameworks, and workload characteristics</p>
            </div>
            
            <div className="flex flex-col items-center text-center relative z-10">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-full flex items-center justify-center mb-5 text-xl font-bold shadow-lg">2</div>
              <h4 className="font-semibold text-blue-300 mb-2">AI Analysis</h4>
              <p className="text-slate-300 text-sm">Our AI extracts technical requirements, memory needs, power specs, and framework dependencies</p>
            </div>
            
            <div className="flex flex-col items-center text-center relative z-10">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-full flex items-center justify-center mb-5 text-xl font-bold shadow-lg">3</div>
              <h4 className="font-semibold text-blue-300 mb-2">Compliance Check</h4>
              <p className="text-slate-300 text-sm">Verify export regulations, regional availability, and certifications for your location</p>
            </div>
            
            <div className="flex flex-col items-center text-center relative z-10">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-full flex items-center justify-center mb-5 text-xl font-bold shadow-lg">4</div>
              <h4 className="font-semibold text-blue-300 mb-2">Advanced Scoring</h4>
              <p className="text-slate-300 text-sm">Hardware options ranked by performance benchmarks, framework compatibility, and value</p>
            </div>
            
            <div className="flex flex-col items-center text-center relative z-10">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-full flex items-center justify-center mb-5 text-xl font-bold shadow-lg">5</div>
              <h4 className="font-semibold text-blue-300 mb-2">Proposal Generation</h4>
              <p className="text-slate-300 text-sm">Receive detailed supplier communications with technical specs and procurement details</p>
            </div>
          </div>
          
          <div className="mt-12 bg-slate-800/50 p-4 rounded-lg">
            <div className="flex items-center text-cyan-400 mb-2">
              <Shield className="w-5 h-5 mr-2" />
              <h4 className="text-sm font-semibold">AI Hardware Platform Benefits</h4>
            </div>
            <div className="grid md:grid-cols-3 gap-4 text-xs">
              <div className="bg-slate-800 p-3 rounded">
                <span className="text-blue-300 font-medium">50%</span> faster procurement process
              </div>
              <div className="bg-slate-800 p-3 rounded">
                <span className="text-blue-300 font-medium">100%</span> export compliance verification
              </div>
              <div className="bg-slate-800 p-3 rounded">
                <span className="text-blue-300 font-medium">30%</span> better performance/price ratio
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-gradient-to-br from-blue-50 to-cyan-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
            Accelerate Your AI Hardware Procurement
          </h2>
          <p className="text-xl mb-8 text-slate-700">
            Get the optimal AI accelerators for your machine learning workloads with our 
            specialized platform that handles technical evaluation, compliance, and supplier matching.
          </p>
          
          {/* Demo Mode Toggle */}
          <div className="flex items-center justify-center mb-10 bg-white p-5 rounded-lg shadow-lg max-w-md mx-auto border border-blue-100">
            <div className="flex items-center space-x-2 mr-4">
              <Cpu className="text-blue-500 w-5 h-5" />
              <Label htmlFor="demo-mode" className="text-base font-medium text-blue-800">
                Demo Mode
              </Label>
            </div>
            <Switch
              id="demo-mode"
              checked={isDemoMode}
              onCheckedChange={toggleDemoMode}
              className="data-[state=checked]:bg-blue-600"
            />
            <p className="ml-4 text-sm text-slate-600">
              {isDemoMode 
                ? "Using AI hardware sample data" 
                : "Using real-time processing"
              }
            </p>
          </div>
          
          <div className="flex flex-wrap gap-4 justify-center">
            <Button 
              size="lg" 
              className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600"
              onClick={() => navigate("/upload")}
            >
              Start AI Hardware Procurement
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              className="text-lg px-8 py-6 border-blue-300 text-blue-700 hover:bg-blue-50"
              onClick={() => navigate("/ai-hardware")}
            >
              Explore Platform Features
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-8 md:mb-0">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent flex items-center">
                <Cpu className="mr-2 h-6 w-6 text-cyan-400" />
                AI Hardware Matchpoint
              </h2>
              <p className="text-slate-300 mt-2">
                Specialized AI accelerator procurement platform
              </p>
              <div className="flex mt-4 space-x-3">
                <div className="bg-slate-800 px-2 py-1 rounded text-xs text-blue-300">GPU</div>
                <div className="bg-slate-800 px-2 py-1 rounded text-xs text-blue-300">TPU</div>
                <div className="bg-slate-800 px-2 py-1 rounded text-xs text-blue-300">NPU</div>
                <div className="bg-slate-800 px-2 py-1 rounded text-xs text-blue-300">IPU</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-x-12 gap-y-4 text-center md:text-left">
              <div>
                <h3 className="text-sm font-semibold text-cyan-400 mb-3">Platform</h3>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Features</a></li>
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Compliance</a></li>
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Benchmarks</a></li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-cyan-400 mb-3">Resources</h3>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Documentation</a></li>
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">API</a></li>
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Support</a></li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-cyan-400 mb-3">Legal</h3>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Privacy Policy</a></li>
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Terms of Service</a></li>
                  <li><a href="#" className="text-slate-300 hover:text-white transition-colors">Contact Us</a></li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-slate-700/50 text-center text-slate-400">
            <p>© {new Date().getFullYear()} AI Hardware Matchpoint. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}