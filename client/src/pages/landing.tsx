import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { FaBolt, FaSearch, FaChartBar, FaFileAlt, FaLaptop, FaMicrochip } from "react-icons/fa";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Cpu } from "lucide-react";
import { useDemoMode } from "@/context/demo-context";

export default function Landing() {
  const [, navigate] = useLocation();
  const { isDemoMode, toggleDemoMode } = useDemoMode();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      {/* Hero Section */}
      <section className="relative py-20 px-6 md:px-10 max-w-7xl mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent rounded-3xl" style={{ zIndex: -1 }}></div>
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold mb-6 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Find the Perfect Supplier for Your RFQ in Any Industry – Fast and Effortless!
            </h1>
            <p className="text-xl mb-8 text-slate-700">
              Our AI-powered platform transforms your RFQ into actionable supplier matches, 
              tailored proposals, and automated communication – saving you time and maximizing efficiency.
            </p>
            <Button 
              size="lg" 
              className="text-lg px-8 py-6"
              onClick={() => navigate("/upload")}
            >
              Get Started
            </Button>
          </div>
          <div className="relative">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-primary/60 rounded-lg opacity-75 blur"></div>
            <div className="relative bg-white p-8 rounded-lg shadow-lg">
              <img 
                src="https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80" 
                alt="Supplier matching process" 
                className="w-full h-auto rounded-md shadow"
              />
              <div className="mt-4 grid grid-cols-5 gap-2">
                <div className="h-2 bg-primary rounded-full"></div>
                <div className="h-2 bg-primary/80 rounded-full"></div>
                <div className="h-2 bg-primary/60 rounded-full"></div>
                <div className="h-2 bg-primary/40 rounded-full"></div>
                <div className="h-2 bg-primary/20 rounded-full"></div>
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
              <h2 className="text-2xl font-bold mb-4 text-red-600">The Problem</h2>
              <p className="text-slate-700">
                Searching for suppliers that meet your RFQ requirements can be time-consuming and inefficient. 
                Whether you're sourcing electronics, manufacturing equipment, or commodities, 
                finding the right match is a challenge.
              </p>
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-4 text-green-600">Our Solution</h2>
              <p className="text-slate-700">
                Upload your RFQ, let our platform analyze your requirements, and instantly find 
                suppliers that match your needs. Score them based on price, quality, and delivery 
                criteria, and send tailored proposals in minutes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-6 bg-gradient-to-b from-slate-100 to-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Killer Features</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-slate-200 hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <FaSearch className="text-primary text-xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Industry-Agnostic Matching</h3>
              <p className="text-slate-600">
                Works for any industry, not just electronics. Whether you need office supplies, 
                industrial equipment, or raw materials.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-slate-200 hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <FaBolt className="text-primary text-xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">RFQ Parsing with AI</h3>
              <p className="text-slate-600">
                Extracts detailed requirements from RFQs using advanced NLP models, 
                no manual input required.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-slate-200 hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <FaChartBar className="text-primary text-xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Supplier Scoring System</h3>
              <p className="text-slate-600">
                Scores suppliers based on weighted criteria like price (50%), 
                quality (30%), and delivery time (20%).
              </p>
            </div>
            
            {/* Feature 4 */}
            <div className="bg-white p-6 rounded-lg shadow-lg border border-slate-200 hover:border-primary/50 transition-all">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <FaFileAlt className="text-primary text-xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Automated Proposals</h3>
              <p className="text-slate-600">
                Generates professional email templates with product details, 
                quantities, and pricing extracted from RFQs.
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
      <section className="py-16 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">How MatchPoint Works</h2>
        
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-center">
            Example: Populating a high school computer class with laptops and monitors
          </h3>
          
          <div className="grid md:grid-cols-5 gap-4 mt-8">
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-xl font-bold">1</div>
              <p className="text-slate-700">Upload the RFQ with detailed specifications</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-xl font-bold">2</div>
              <p className="text-slate-700">AI extracts key requirements and specifications</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-xl font-bold">3</div>
              <p className="text-slate-700">Platform matches with suitable suppliers</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-xl font-bold">4</div>
              <p className="text-slate-700">Suppliers are scored based on your criteria</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-xl font-bold">5</div>
              <p className="text-slate-700">Tailored proposals are generated and ready to send</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-6 bg-gradient-to-r from-primary/20 to-primary/5">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">Try it now – Find the perfect supplier today!</h2>
          <p className="text-xl mb-6 text-slate-700">
            Upload your RFQ and let MatchPoint do the hard work for you.
          </p>
          
          {/* Demo Mode Toggle */}
          <div className="flex items-center justify-center mb-8 bg-white p-4 rounded-lg shadow-sm max-w-md mx-auto">
            <div className="flex items-center space-x-2 mr-4">
              <FaLaptop className="text-primary" />
              <Label htmlFor="demo-mode" className="text-base font-medium">
                Demo Mode
              </Label>
            </div>
            <Switch
              id="demo-mode"
              checked={isDemoMode}
              onCheckedChange={toggleDemoMode}
            />
            <p className="ml-4 text-sm text-gray-500">
              {isDemoMode 
                ? "Using sample data for demonstration" 
                : "Using real-time processing"
              }
            </p>
          </div>
          
          <Button 
            size="lg" 
            className="text-lg px-8 py-6"
            onClick={() => navigate("/upload")}
          >
            Get Started
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-slate-900 text-white">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                MatchPoint
              </h2>
              <p className="text-slate-300 mt-2">
                AI-powered supplier matching for any industry
              </p>
            </div>
            
            <div className="flex space-x-6">
              <a href="#" className="text-white hover:text-primary transition-colors">Privacy Policy</a>
              <a href="#" className="text-white hover:text-primary transition-colors">Terms of Service</a>
              <a href="#" className="text-white hover:text-primary transition-colors">Contact Us</a>
            </div>
          </div>
          
          <div className="mt-8 text-center text-slate-400">
            <p>© {new Date().getFullYear()} MatchPoint. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}