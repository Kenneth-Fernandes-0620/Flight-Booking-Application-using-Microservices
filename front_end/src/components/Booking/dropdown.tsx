const Dropdown = ({ dropdown, toggleDropdown, defaultValue, options, dropDownType, updateValue }: { dropdown: boolean, toggleDropdown: () => void, defaultValue: string, options: string[], dropDownType: DropdownType, updateValue: React.Dispatch<React.SetStateAction<string>> }) => {
    return (
        <div className="relative inline-block text-left w-full">

            {
                dropDownType === DropdownType.DATE &&
                <input
                    aria-label="Date"
                    type="date"
                    min={new Date().toISOString().split("T")[0]}
                    value={defaultValue}
                    className="block justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                    onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                        const [year, month, day] = event.target.value.split('-');
                        updateValue(`${year}-${month}-${day}`);
                        toggleDropdown();
                    }} />
            }
            {
                (dropDownType === DropdownType.TEXT || dropDownType === DropdownType.NUMBER) &&
                <button
                    id="dropdownButton"
                    onClick={toggleDropdown}
                    className="inline-flex justify-between w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                    {defaultValue}
                    <svg
                        className="-mr-1 ml-2 h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                </button>
            }

            {dropdown && dropDownType != DropdownType.DATE && (
                <div className="origin-top-right absolute right-0 mt-2 w-56 max-h-60 overflow-auto rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                    <div className="py-1">
                        {
                            dropDownType === DropdownType.TEXT &&
                            options.map((option) => {
                                return (
                                    <button key={option} className="block px-4 py-2 w-full text-sm text-left text-gray-700 hover:bg-gray-100"
                                        onClick={() => {
                                            updateValue(option);
                                            toggleDropdown();
                                        }}
                                    >
                                        {option}
                                    </button>
                                );
                            })
                            ||
                            dropDownType === DropdownType.NUMBER &&
                            [...Array(4).keys()].map((option) => {
                                return (
                                    <button key={option + 1} className="block px-4 py-2 w-full text-sm text-left text-gray-700 hover:bg-gray-100"
                                        onClick={() => {
                                            updateValue(`${option + 1}`);
                                            toggleDropdown();
                                        }}
                                    >
                                        {option + 1}
                                    </button>
                                );
                            })
                        }
                    </div>
                </div>
            )}
        </div>
    );
}


// create a enum for the dropdown types
enum DropdownType {
    TEXT,
    DATE,
    NUMBER
}

export default Dropdown;
export { DropdownType };