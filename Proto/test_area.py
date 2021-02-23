#(lambda checked, index=i:button.furnace_button_click(self.stk_w, index+1))
#(lambda:button.furnace_button_click(self.stk_w, i+1))

def get_index(i):
    print('test')
    print(i)

some_list = []
for i in range(8):
    lambda checked, i=i:get_index(i)
