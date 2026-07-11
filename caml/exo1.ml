
(* let last2 x = if x = [] then option None else option Some x[List.length(x.length];; *)


(*
Solution:
*)

let rec last = function 
  | [] -> None
  | [ x ] -> Some x
  | _ :: t -> last t;;

(* val last : 'a list -> 'a option = <fun> *)

last([1;2;3]);;
(*  - : int option = Some 3 *)
(* print_int( last([1;2;3]) );; *) (* error it's int option et on doit afficher que du option *)


let rec last_two = function 
    | [] | [_] -> None
    | [x; y] -> Some (x,y)
    | _ :: t -> last_two t;;
    
let rec at k = function
    | [] -> None
    | h :: t -> if k = 0 then Some h else at (k - 1) t;;
(* val at : int -> 'a list -> 'a option = <fun> *)

let rec len = function
    | [] -> 0
    | h :: t -> 1+len(t);;
    
(* en version tail recursive (moins de place sur la stack) *)

let length list =
    let rec aux n = function
      | [] -> n
      | _ :: t -> aux (n + 1) t
    in
    aux 0 list;;
(* val length : 'a list -> int = <fun> *)

(*
Reverse a list.

OCaml standard library has List.rev but we ask that you reimplement it.

# rev ["a"; "b"; "c"];;
- : string list = ["c"; "b"; "a"]
*)

(*
let rec rev = function
   | [] -> []
   | x :: t -> rev(t) :: x;;
   
rev ["a"; "b"; "c"];;

*)

let rev list =
    let rec aux acc = function
      | [] -> acc
      | h :: t -> aux (h :: acc) t
    in
    aux [] list;;
(* val rev : 'a list -> 'a list = <fun> *)

    
