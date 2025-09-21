import React from 'react'



interface ListItemProps {
    icon: React.ReactNode
    title: string
    description: string
    color: string
}
  
const ListItem = ({title, description, color, icon}: ListItemProps) => {
  return (

          <div className="text-left w-full bg-[#1E1E1E]  border border-[#1b1b1b]  rounded-[20px] px-[12px] py-[20px] md:p-[12px]">
            <div className="flex items-start flex-col  md:flex-row gap-2 space-x-4">
              <div className={`w-10 h-10 ${color} border rounded-lg flex items-center justify-center flex-shrink-0`}>
                <div className="text-primary text-md">{icon}</div>
              </div>
              <div className="flex-1">
                
                  <h3 className="text-base font-semibold text-white">{title}</h3>
              
                <p className="text-[#B1B1B1] text-base">{description}</p>
              </div>
            </div>
          </div>
    
  )
}

export default ListItem