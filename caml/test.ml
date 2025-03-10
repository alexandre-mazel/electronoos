let carre x = x * x;;
print_int(carre(3));
print_string "\n";;

let succ x = x + 1;;
let pred = fun x -> x - 1;;

print_int(succ(3));;
print_string "\n";;
print_int(pred(3));;
print_string "\n";;

Printf.printf "%B", 1=1;;

let pythagore x y z = let carre n = n*n in carre x + carre y = carre z;;
(* print_bool(pythagore 2 3 4);; *)

print_string "Array start:\n";;

let a0 = Array.make 10 0;;
 
 let a = [| 1; 2; 3; 4 |];;
 print_int a.(3);
 print_string "\n";
 a.(3)<-5;
 print_int a.(3);
 print_string "\n";;
 
 type complexe = { re : float; im : float };;
 
 let nbr = { re = 1.0; im =-1.0 };;
 print_float nbr.re;;
 
 "buenos dias".[4];; (* .[] for char et .() for list *)
 
 let z = 2. *. 3. (* *. c'est la multiplication flottante)