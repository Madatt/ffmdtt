Toy lexer, parser and compilator to pseudo-assembly I wrote when learning about compilers.



```
def f32 add_mul(f32 arg1; u32 arg2)
{
    u32 c = arg1 * arg2 / (arg1 + arg2);
    if(c) {
        u32 h = c / c;
        if(h / c) {
            return h;
        }
    }

    return c;
}
```
to ->
```
add_mul:
    alloc    2    
    load_a    0    
    load_a    1    
    itof        
    f32mul        
    load_a    0    
    load_a    1    
    itof        
    f32add        
    f32div        
    ftoi        
    set    0    
    load    0    
    if_not    add_mul_0    
    load    0    
    load    0    
    u32div        
    set    1    
    load    1    
    load    0    
    u32div        
    if_not    add_mul_1    
    load    1    
    itof        
    ret        
add_mul_1:
add_mul_0:
    load    0    
    itof        
    ret        

```
