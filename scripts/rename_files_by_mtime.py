import os
import sys
import re


def rename_files_by_mtime_chatgpt_moche(path: str) -> None:
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(path, f)))

    pattern = re.compile(r'^(\d+)_')

    indexed = [(f, f"{i:03d}_") for i, f in enumerate(files, 1)]

    current_numbers = [
        int(m.group(1))
        for f, _ in indexed
        if (m := pattern.match(f))
    ]

    consistent = current_numbers == list(range(1, len(current_numbers) + 1))

    for f, prefix in indexed:
        old_path = os.path.join(path, f)
        m = pattern.match(f)

        if m:
            if consistent:
                continue
            new_name = pattern.sub(prefix, f)
        else:
            new_name = prefix + f

        new_path = os.path.join(path, new_name)
        print( "INF: renaming file '%s' to '%s'" % (old_path, new_path) )
        #~ os.rename(old_path, new_path)
        
def rename_files_by_mtime(path: str) -> None:
    
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    
    files.sort(key=lambda f: os.path.getmtime(os.path.join(path, f)))
    
    last_value = 0
    cpt_renammed = 0
    
    for f in files:
        old_path = os.path.join(path, f)
        
        print( "f: ", f )

        if f[0].isdigit() and f[1].isdigit() and f[2].isdigit() and f[3] == "_":
            value = int( f[:3] )
            print( "last_value: ", last_value )
            print( "value: ", value )
            
            if value > last_value or 1: # meme si c'est pas le bon ordre, ca passe
                #~ last_value = value
                last_value = max(value,last_value)
                continue

            
        else:
            last_value += 2
            prefix = "%03d_" % (last_value)
            new_name = prefix + f

        new_path = os.path.join(path, new_name)
        print( "INF: renaming file '%s' to '%s'" % (old_path, new_path) )
        if 1:
            # really renamming
            os.rename(old_path, new_path)
        cpt_renammed += 1
        
    print( "INF: cpt_renammed: %d" % cpt_renammed )


if __name__ == "__main__":
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."
    rename_files_by_mtime(target_path)