import Button  from "@/components/ui/Button"

const  Header =() =>{
  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
                  {/* <span className="text-2xl font-bold text-foreground">Konnect</span> */}
                  <img src="/images/logo.png" alt="Konnect" width={50}/>
        </div>

      

              <div className="flex items-center space-x-4">
              <nav className="hidden md:flex items-center space-x-8">
          <a href="#docs" className="text-muted-foreground hover:text-foreground transition-colors">
            Docs
          </a>
        </nav>
          <Button variant="konnect" size="lg">
          Download App
          </Button>
        </div>
      </div>
    </header>
  )
}

export default Header